# Infrastructure Accessibility Benefit Scoring (IABS)

This project scores real estate listings in the Mumbai Metropolitan Region (MMR) based on their proximity to key infrastructure assets using open geospatial data and outputs an interpretable score called the **Infrastructure Accessibility Benefit Score (IABS)**.

---

## 🔧 Folder Structure

```
iabs-project/
│
├── iabs-methodology.md         # Methodology document
├── infra-scoring.py            # Main scoring Python script
├── analysis.ipynb              # Jupyter notebook for exploration & visualization
│
├── data/
│   ├── mumbai-house-price-data-cleaned.csv
│   ├── mmr-infra-geo.json
│   └── infra-scored-properties.csv
│
└── visuals/
    └── infra-score-map.html    # Folium map with coloured infra scoring
```

---

## 🚀 Quick Start

1. **Clone the repo** (after creating one on GitHub):
   ```bash
   git clone https://github.com/yourusername/iabs-project.git
   cd iabs-project
   ```

2. **Install dependencies**:
   ```bash
   pip install pandas numpy requests tqdm plotly folium
   ```

3. **Run scoring** (optional to re-run):
   ```bash
   python infra-scoring.py
   ```

4. **Launch Jupyter notebook**:
   ```bash
   jupyter notebook analysis.ipynb
   ```

---

## 📍 Features

- Scores each property from 0 to 100 based on its proximity to:
  - Metro Stations
  - Bus Depots
  - Highways
  - Airports
- Uses Haversine distance and NumPy vectorization for fast computation.
- Generates HTML maps with **Folium** and interactive visuals using **Plotly**.
- Outputs merged datasets for further modeling or dashboards.

---

## 📊 Sample Outputs

| locality     | BHK | price_per_sqft | metro_score | IABS |
|--------------|-----|----------------|-------------|------|
| Andheri East | 2   | ₹19,000        | 1.0         | 92.3 |
| Bhandup West | 1   | ₹14,500        | 0.5         | 63.2 |

> Infra score visualized on Folium map in can be found in the `visuals` folder.

---

## ⚠️ Limitations

- Pure distance-based scoring — doesn't account for road network or travel time.
- OSM data completeness may vary by region.
- Doesn't yet include schools, hospitals, or employment clusters.
- Assumes equal impact of proximity on all property types.

---

## 📌 Applications

- Real estate valuation models
- Urban planning dashboards
- Market accessibility analysis
- Buyer-facing property filters

---

## 📃 License

MIT License