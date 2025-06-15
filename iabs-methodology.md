# Infrastructure Accessibility Benefit Scoring Methodology (IABS)

This document outlines the methodology for evaluating and scoring real estate listings based on their proximity to key infrastructure assets in the Mumbai Metropolitan Region (MMR). The result is a normalized, interpretable **Infrastructure Accessibility Benefit Score (IABS)** that helps identify listings with superior location-based connectivity.

---

## Objectives

- Quantify how well-connected a property is to core urban infrastructure.
- Create a scalable, interpretable score between **0 and 100**.
- Use publicly available geospatial data (OpenStreetMap + custom assets) for infrastructure locations.

---

## Covered Infrastructure Types

The following infrastructure types are considered:

1. **Metro Stations** (`railway=station`, `station=subway|light_rail`, custom metro types)  
2. **Bus Depots** (`amenity=bus_station`, `bus=terminal`, custom)  
3. **Highways/Expressways** (`highway=motorway|trunk|primary|secondary`, custom)  
4. **Airports** (`aeroway=aerodrome|terminal`)  

These assets are chosen based on impact on urban mobility and property value.

---

## Step 1: Define Property Dataset Boundary

- Load the full property dataset with latitude and longitude.  
- Identify the four extremities: Northeast, Southwest, Northwest, Southeast.  
- Use these to define a bounding box with a margin (e.g., ±0.05) for querying infrastructure data from OpenStreetMap (OSM).  

---

## Step 2: Infra Asset Extraction (Hybrid)

Two methods are combined:

### 2A. Static Custom Infra Assets (JSON)  
A curated JSON file with ~75+ infra assets manually compiled.

### 2B. Dynamic OpenStreetMap Query  
Use Overpass API to query within the bounding box for:  
- Metro: `railway=station` (with `station=subway|light_rail` tags)  
- Bus Depots: `amenity=bus_station`  
- Highways: `highway in [motorway, trunk, primary, secondary]`  
- Airports: `aeroway in [aerodrome, terminal]`  

Both are merged and deduplicated based on coordinates and `type+name`.

Final output is stored in `mmr-infra-geo.json`:

```json
{
  "name": "Ghatkopar Metro Station",
  "type": "metro",
  "coordinates": [19.0853, 72.9086]
}
````

---

## Step 3: Proximity Computation (Haversine-Based)

* For each property, compute the haversine distance to each infra asset.
* Only keep the nearest asset of each type **within cutoff distance**.

---

## Step 4: Distance Thresholds (Updated)

| Infra Type | Max Range (km) |
| ---------- | -------------- |
| Metro      | 3.0            |
| Bus Depot  | 3.0            |
| Highway    | 3.0            |
| Airport    | 5.0            |

---

## Step 5: Assign Proximity Scores (Per Asset Type)

| Distance Range             | Metro Score | Bus Score | Highway Score | Airport Score |
| -------------------------- | ----------- | --------- | ------------- | ------------- |
| 0–350 m                    | 1.0         | 1.0       | 1.0           | 1.0           |
| 351–750 m                  | 0.8         | 0.7       | 1.0           | 1.0           |
| 751–1500 m                 | 0.5         | 0.4       | 0.6           | 0.8           |
| 1501–3000 m                | 0.2         | 0.1       | 0.3           | 0.6           |
| 3001–5000 m (airport only) | -           | -         | -             | 0.3           |
| > cutoffs                  | 0.0         | 0.0       | 0.0           | 0.0           |

---

## Step 6: Weighting and Final Scoring

Weights are applied to reflect the importance of each infrastructure type:

| Infra Type | Weight |
| ---------- | ------ |
| Metro      | 0.40   |
| Bus Depot  | 0.25   |
| Highway    | 0.20   |
| Airport    | 0.15   |

Formula:

```
Infra_Score = (
  0.40 * Metro_Score +
  0.25 * Bus_Score +
  0.20 * Highway_Score +
  0.15 * Airport_Score
)
```

Multiply by 100 and round for **Infrastructure Accessibility Benefit Score (IABS)** on a 0–100 scale.

---

## Step 7: Output Data Structure

| property\_id | latitude | longitude | metro\_score | bus\_score | hwy\_score | airport\_score | IABS |
| ------------ | -------- | --------- | ------------ | ---------- | ---------- | -------------- | ---- |
| 1001         | 19.07    | 72.88     | 1.0          | 0.4        | 0.6        | 0.3            | 70.5 |
| 1002         | 19.03    | 72.95     | 0.2          | 1.0        | 0.3        | 0.0            | 48.5 |

---

## Notes and Optimizations

* Uses **NumPy vectorization** for memory-efficient distance computation.
* Future enhancement: switch to **travel time** using local GTFS or public transport APIs.
* Uses **merged and deduplicated** infra assets from static JSON and OSM.

---

## Applications

* Detect under/overvalued listings based on connectivity.
* Rank or filter listings in dashboards.
* Integrate with valuation models as a location-accessibility feature.
* Overlay on maps for visual analytics.

---

## Limitations

While the IABS is useful, it has key limitations:

1. **Straight-Line Distance Only**
   The model uses Haversine distance (as-the-crow-flies), which ignores actual road networks, obstructions, or pedestrian accessibility.

2. **Fixed Score Thresholds**
   All properties are scored using hardcoded distance bins that may not adapt to actual city layouts, density, or user preferences.

3. **Equal Weighting Across the Region**
   The weights are uniform across MMR. Localities with high reliance on one transport mode aren't treated differently.

4. **No Traffic or Schedule Data**
   Infra quality or congestion (e.g., a crowded metro line or poor bus frequency) is not considered.

5. **No Socioeconomic or Urban Quality Factors**
   The approach ignores aspects like neighborhood safety, walkability, or cleanliness.

6. **Data Limitations**
   OpenStreetMap and Overpass API may miss new or untagged infra. Some real assets may not be captured.

7. **Airport Scoring Is Naively Applied**
   Airports affect property value differently based on noise zones, distance buffers, etc., which are not modeled.

8. **Construction or Future Assets Ignored**
   Infra under construction or approved projects are not factored in.

---