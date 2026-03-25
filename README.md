# 🚦 Kochi Traffic Intelligence

A machine learning dashboard predicting real-time traffic congestion and accident risk across 58 roads in 7 areas of Kochi, Kerala. Built with XGBoost, Streamlit, and Folium. Users select area, time, day and weather to get colour-coded map forecasts with weather metrics and danger alerts.

---

## Overview

Kochi Traffic Intelligence is an end-to-end ML project that models urban traffic behaviour across Kochi's major road network. The system takes user inputs — area, day of week, hour, and weather condition — and runs two trained XGBoost classifiers to predict the **congestion level** and **accident risk level** for every road in the selected area. Results are visualised on an interactive dark-map overlay with colour-coded markers, a sortable road table, and a live weather and risk summary panel.

The project is designed in two phases. The current version runs on a synthetic dataset that mirrors the schema of real TomTom Traffic API and OpenWeatherMap data. The second phase replaces the synthetic data with real collected data — requiring only a model retrain with no changes to the dashboard or pipeline.

---

## Features

- **Congestion prediction** — classifies each road as Low, Moderate, High, or Very High congestion using 23 engineered features including cyclic time encoding, speed ratio, and weather multipliers
- **Accident risk prediction** — models relative risk as a function of congestion severity, weather condition, speed deviation, and time of day
- **Interactive map** — Folium-powered dark/light map with clickable markers showing per-road stats
- **Weather panel** — displays temperature, rainfall, visibility, and humidity derived from the selected weather condition
- **Danger alerts** — highlights roads with High or Very High readings in both congestion and risk
- **Dark / Light mode** — full theme toggle including map tile switching between CartoDB Dark Matter and CartoDB Positron
- **7 areas, 58 roads** — covers Edappally, Kakkanad, Fort Kochi, Mattancherry, Vyttila, Palarivattom, and Kadavanthra

---

## Project Structure

```
kochi_traffic/
├── app.py                          # Streamlit dashboard (main entry point)
├── config.py                       # Road names, coordinates, properties, colour maps
├── data_utils.py                   # Feature engineering and model loading
├── predictor.py                    # Runs both ML models across all roads in an area
├── maps.py                         # Folium map generation (congestion + risk)
├── requirements.txt                # Python dependencies
├── generate_dataset.py             # Generates the synthetic training CSV
├── augment_weather.py              # Pads real data with synthetic rain/fog rows
├── train.py                        # Trains both ML models, saves to models/ folder
├── models/                         # Trained .pkl files (created by train.py)
│   ├── congestion_model.pkl
│   ├── accident_risk_model.pkl
│   ├── label_encoders.pkl
│   ├── feature_columns.pkl
│   ├── risk_feature_columns.pkl
│   └── class_orders.pkl
├── kochi_traffic_synthetic_v2.csv  # Synthetic training dataset (38,304 rows)
└── kochi_traffic_ml_v2.ipynb       # Legacy Google Colab notebook (optional)
```

---

## Dataset

The synthetic dataset (`kochi_traffic_synthetic_v2.csv`) contains **38,304 rows** across 14 days, sampled every 30 minutes for all 58 roads. It is designed to exactly match the schema of real data collected via the TomTom Traffic Flow API and OpenWeatherMap API.

### Schema (27 columns)

| Column | Description |
|--------|-------------|
| `timestamp` | Full datetime of the reading |
| `date` | Date string (YYYY-MM-DD) |
| `day_of_week` | Monday–Sunday |
| `hour` / `minute` | Time components |
| `time_period` | HH:MM string |
| `area` | One of 7 Kochi areas |
| `road_name` | Named road (58 total) |
| `road_type` | Highway / Arterial / Local |
| `lanes` | Number of lanes |
| `speed_limit_kmph` | Posted speed limit |
| `weather_condition` | Clear / Cloudy / Light Rain / Heavy Rain / Fog |
| `rainfall_mm` | Rainfall in millimetres |
| `visibility_m` | Visibility in metres |
| `temperature_c` | Temperature in Celsius |
| `humidity_pct` | Relative humidity percentage |
| `current_speed_kmph` | Observed average speed |
| `free_flow_speed_kmph` | Speed under no-congestion conditions |
| `congestion_score` | 0–1 continuous congestion index |
| `congestion_level` | Low / Moderate / High / Very High |
| `vehicle_volume_est` | Estimated vehicles per hour |
| `accident_risk_score` | 0–1 modelled risk index |
| `accident_risk_level` | Low / Moderate / High / Very High |
| `is_rush_hour` | 1 if 07:00–09:00 or 17:00–20:00 |
| `is_weekend` | 1 if Saturday or Sunday |
| `is_night` | 1 if 22:00–05:00 |
| `data_source` | `synthetic` or `real` |
| `tomtom_confidence` | TomTom confidence score (0.75–1.0) |

### Weather distribution (Kerala-weighted)
- Clear: 28% — Cloudy: 22% — Light Rain: 25% — Heavy Rain: 15% — Fog: 10%

### Congestion derivation
```
congestion_score = 1 - (current_speed / free_flow_speed)
```

### Accident risk derivation
Accident risk is a **modelled estimate** — not recorded accident data. It is derived from congestion severity, weather condition multiplier, speed deviation above the posted limit, and a night-time bonus. This is consistent with standard traffic safety modelling practice where risk is inferred from observable road conditions rather than waiting for incidents to occur.

---

## ML Models

Both models are trained in `kochi_traffic_ml_v2.ipynb` using **XGBoost** multi-class classification.

### Congestion Model
- **Target:** `congestion_level` (4 classes)
- **Features:** 23 features including cyclic hour/day encoding, speed ratio, road type, weather condition, rainfall, visibility, temperature, humidity, and location encodings
- **Training:** 80/20 train-test split, stratified

### Accident Risk Model
- **Target:** `accident_risk_level` (4 classes)
- **Features:** Same 23 features plus `congestion_score` and `congestion_level_enc`
- **Class balancing:** SMOTE oversampling applied to minority classes
- **Training:** 80/20 split

### Feature engineering
- **Cyclic encoding** — hour and day encoded as sin/cos pairs to preserve circular continuity (e.g. 23:00 is close to 00:00)
- **Speed ratio** — `current_speed / free_flow_speed`, captures deviation from normal flow
- **Label encoding** — area, road name, road type, weather condition encoded with sklearn LabelEncoder; encoders saved for inference

---

## Setup & Running

### 1. Train the models (Google Colab)

1. Open `kochi_traffic_ml_v2.ipynb` in [Google Colab](https://colab.research.google.com)
2. Run **Cell 1** to install dependencies
3. Run **Cell 2** — a file picker will appear, upload `kochi_traffic_synthetic_v2.csv`
4. Run all remaining cells in order
5. Run the final cell to download `kochi_traffic_models_v2.zip`
6. Extract the zip — you will get 6 `.pkl` files

### 2. Set up the dashboard

```bash
# Clone or download the project files
# Place the 6 .pkl files into a models/ folder

pip install -r requirements.txt
streamlit run app.py
```

### 3. Using the dashboard

- Select **Day**, **Hour**, **Weather**, and **Location** from the sidebar
- Click **⚡ ANALYSE TRAFFIC**
- Switch between **Congestion** and **Risk** map tabs
- Click any marker on the map for per-road details
- Use the theme toggle at the top of the sidebar to switch between dark and light mode

---

## Swapping to Real Data (Phase 2)

When real data collection is complete, follow these steps:

### Step 1 — Check your weather coverage

Run `python status.py` on the phone and check the weather breakdown. If any of Light Rain, Heavy Rain, or Fog is below ~8% of total rows, proceed to Step 2. If coverage looks good, skip to Step 3.

### Step 2 — Augment with rain/fog rows (if needed)

Real data collected during dry spells will be underrepresented in rain/fog conditions. Use `augment_weather.py` to pad the dataset:

```bash
# Download kochi_traffic_real.csv from GitHub first, then:
python augment_weather.py --real kochi_traffic_real.csv --out kochi_traffic_augmented.csv
```

This generates synthetic rain/fog rows so each weather condition reaches at least 8% of the total. Real rows keep `data_source = "real"`, synthetic rows are tagged `data_source = "synthetic"`.

Options:
- `--target 10` — raise the target percentage (default: 8)
- `--seed 42` — set random seed for reproducibility

### Step 3 — Retrain locally

```bash
# With augmented data (recommended):
python train.py --data kochi_traffic_augmented.csv

# With raw real data (if weather coverage is good):
python train.py --data kochi_traffic_real.csv

# Skip EDA/confusion matrix plots if you just want speed:
python train.py --data kochi_traffic_augmented.csv --no-plots
```

Models are saved directly into `models/` — no downloading or file moving needed.

### Step 4 — Restart the dashboard

```bash
streamlit run app.py
```

`train.py` saves directly into `models/` — no file moving or extraction needed. Just restart the dashboard.

---

## Areas & Roads Covered

| Area | Roads |
|------|-------|
| **Edappally** | NH 66 Bypass, Edappally Junction, Seaport Airport Road, Edappally Toll Junction, Rajagiri Road, Edappally North, Konthuruthy Road, LuLu Mall Access Road |
| **Kakkanad** | Kakkanad Main Road, Infopark Expressway, Infopark Road Phase 1 & 2, Thrippunithura Road, CSEZ Road, Kolenchery Road, High Court Road Kakkanad |
| **Fort Kochi** | Beach Road, Ridsdale Road, Calvathy Road, Tower Road, Princess Street, Napier Street, Fort Kochi Ferry Road, Willingdon Island Road |
| **Mattancherry** | Mattancherry Road, Jew Town Road, Bazaar Road, Pallipuram Road, Dutch Cemetery Road, Thoppumpady Road, Mattancherry Palace Road, Harbour Road |
| **Vyttila** | NH 66 Vyttila, Vyttila Junction, Kundannoor Bridge Road, Vyttila Mobility Hub Road, Aroor Bypass, Chilavannoor Road, Pachalam Road, SA Road Vyttila |
| **Palarivattom** | Palarivattom Junction, NH 85, Kaloor–Palarivattom Rd, Banerji Road, Vyttila–Palarivattom Rd, Pullepady Road, Elamkulam Road |
| **Kadavanthra** | Kadavanthra Junction, MG Road, Shanmugham Road, SA Road, Ravipuram Road, Chittoor Road, Convent Road, Judges Avenue, Bristow Road, Kasturi Ranga Rd |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Dashboard | Streamlit |
| ML Models | XGBoost, scikit-learn, imbalanced-learn |
| Maps | Folium (CartoDB tiles) |
| Data | Pandas, NumPy |
| Training | Google Colab |
| Real data collection | TomTom Traffic Flow API, OpenWeatherMap API |

---

## Limitations

- **Accident risk is modelled, not recorded** — the system estimates relative risk from traffic and weather inputs. It does not use historical accident records.
- **Synthetic data** — the current version is trained on generated data. Predictions will improve significantly once real collected data is used for training.
- **Static inference** — predictions are based on the selected inputs, not a live feed. The dashboard does not auto-refresh.
- **Road coordinates** — major junctions are verified against OpenStreetMap. Smaller local roads are approximate and may be offset by up to 100–200 metres.
