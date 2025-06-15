import pandas as pd
import numpy as np
import json
import requests
from tqdm import tqdm

def download_infra_assets_from_overpass(input_csv, output_json):
    df = pd.read_csv(input_csv)
    north, south = df['latitude'].max(), df['latitude'].min()
    east, west = df['longitude'].max(), df['longitude'].min()
    bbox = f"{south},{west},{north},{east}"

    query = f"""
    [out:json][timeout:100];
    (
      node["railway"="station"]({bbox});
      node["amenity"="bus_station"]({bbox});
      way["highway"~"motorway|trunk"]({bbox});
      node["aeroway"~"aerodrome|terminal"]({bbox});
    );
    out center;
    """

    response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query})
    data = response.json()

    results = []
    for element in data['elements']:
        try:
            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')
            tags = element.get('tags', {})
            name = tags.get('name', 'Unnamed')
            if 'railway' in tags:
                itype = 'Metro Station'
            elif 'amenity' in tags:
                itype = 'Bus Depot'
            elif 'aeroway' in tags:
                itype = 'Airport'
            elif 'highway' in tags:
                itype = 'Highway'
            else:
                continue
            results.append({
                "name": name,
                "type": itype,
                "coordinates": [lat, lon],
                "description": tags,
                "region": ""
            })
        except:
            continue

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

def haversine_np(lat1, lon1, lat2, lon2):
    R = 6371
    lat1 = np.radians(lat1)[:, np.newaxis]
    lon1 = np.radians(lon1)[:, np.newaxis]
    lat2 = np.radians(lat2)[np.newaxis, :]
    lon2 = np.radians(lon2)[np.newaxis, :]
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def score_distance(distances, itype):
    if itype == 'Airport':
        bins = [0, 0.35, 0.75, 1.5, 2.0, 5.0]
        scores = [1.0, 1.0, 0.8, 0.6, 0.3, 0.0]
    else:
        bins = [0, 0.35, 0.75, 1.5, 2.0]
        scores = [1.0, 0.8, 0.5, 0.2, 0.0, 0.0]
    
    dist_bin = np.digitize(distances, bins, right=True)
    dist_bin = np.clip(dist_bin, 0, len(scores) - 1)
    score_map = np.array(scores)
    return score_map[dist_bin]

def score_properties(input_csv, infra_json, output_csv, batch_size=500, sample_percent=100):
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=['latitude', 'longitude']).reset_index(drop=True)

    # Sample subset
    if 0 < sample_percent < 100:
        limit = int(len(df) * sample_percent / 100)
        df = df.iloc[:limit].copy()

    with open(infra_json, 'r') as f:
        infra = json.load(f)

    infra_by_type = {
        'Metro Station': [],
        'Bus Depot': [],
        'Highway': [],
        'Airport': []
    }
    for item in infra:
        if item['type'] in infra_by_type:
            infra_by_type[item['type']].append(item)

    weights = {
        'Metro Station': 0.4,
        'Bus Depot': 0.25,
        'Highway': 0.2,
        'Airport': 0.15
    }

    result_batches = []

    for start in tqdm(range(0, len(df), batch_size)):
        end = min(start + batch_size, len(df))
        batch = df.iloc[start:end].copy()
        prop_lat = batch['latitude'].values
        prop_lon = batch['longitude'].values

        scores = {
            'metro_score': np.zeros(len(batch)),
            'bus_score': np.zeros(len(batch)),
            'hwy_score': np.zeros(len(batch)),
            'airport_score': np.zeros(len(batch)),
        }

        for itype, weight in weights.items():
            infra_points = infra_by_type[itype]
            if not infra_points:
                continue
            infra_lats = np.array([x['coordinates'][0] for x in infra_points])
            infra_lons = np.array([x['coordinates'][1] for x in infra_points])

            dists = haversine_np(prop_lat, prop_lon, infra_lats, infra_lons)
            min_dists = np.min(dists, axis=1)
            scores_key = {
                'Metro Station': 'metro_score',
                'Bus Depot': 'bus_score',
                'Highway': 'hwy_score',
                'Airport': 'airport_score'
            }[itype]
            scores[scores_key] = score_distance(min_dists, itype)

        batch['metro_score'] = scores['metro_score']
        batch['bus_score'] = scores['bus_score']
        batch['hwy_score'] = scores['hwy_score']
        batch['airport_score'] = scores['airport_score']
        batch['IABS'] = (
            scores['metro_score'] * weights['Metro Station'] +
            scores['bus_score'] * weights['Bus Depot'] +
            scores['hwy_score'] * weights['Highway'] +
            scores['airport_score'] * weights['Airport']
        ) * 100

        result_batches.append(batch)

    pd.concat(result_batches).to_csv(output_csv, index=False)

# Usage
if __name__ == "__main__":
    input_file = "./data/mumbai-house-price-data-cleaned.csv"
    infra_file = "./data/mmr-infra-geo.json"
    output_file = "./data/infra-scored-properties.csv"

    # Optional: download fresh infra data
    # download_infra_assets_from_overpass(input_file, infra_file)

    # Sample 50% of data; use 100 for full dataset
    score_properties(input_file, infra_file, output_file, sample_percent=25)
