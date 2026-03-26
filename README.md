# 🚦 Kochi Traffic Intelligence

A machine learning dashboard predicting real-time traffic congestion and accident risk across 58 roads in 7 areas of Kochi, Kerala. Built with XGBoost, Streamlit, and Folium. Users select area, time, day and weather to get colour-coded map forecasts with weather metrics and danger alerts.

---

## Overview

Kochi Traffic Intelligence is an end-to-end ML project that models urban traffic behaviour across Kochi's major road network. The system takes user inputs — area, day of week, hour, and weather condition — and runs two trained XGBoost classifiers to predict the **congestion level** and **accident risk level** for every road in the selected area. Results are visualised on an interactive dark-map overlay with colour-coded markers, a sortable road table, and a live weather and risk summary panel.

Real traffic data is collected every 30 minutes via an Android phone running Termux, querying the TomTom Traffic Flow API and OpenWeatherMap API, and auto-committing to a private GitHub repository. Because the real data was collected during a dry spell, rain and fog rows are supplemented using `augment_weather.py` before retraining.

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
├── train.py                        # Trains both ML models, saves to models/ folder
├── generate_dataset.py             # Generates the synthetic training CSV
├── augment_weather.py              # Pads real data with synthetic rain/fog rows
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── models/                         # Trained .pkl files (created by train.py)
    ├── congestion_model.pkl
    ├── accident_risk_model.pkl
    ├── label_encoders.pkl
    ├── feature_columns.pkl
    ├── risk_feature_columns.pkl
    └── class_orders.pkl
```

---

## Dataset Schema (27 columns)

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

### Congestion derivation
```
congestion_score = 1 - (current_speed / free_flow_speed)
```

### Accident risk derivation
Accident risk is a **modelled estimate** — not recorded accident data. It is derived from congestion severity, weather condition multiplier, speed deviation above the posted limit, and a night-time bonus.

---

## ML Models

Both models are trained using `train.py` with **XGBoost** multi-class classification.

### Congestion Model
- **Target:** `congestion_level` (4 classes: Low / Moderate / High / Very High)
- **Features:** 23 features including cyclic hour/day encoding, speed ratio, road type, weather variables, and location encodings
- **Training:** 80/20 stratified split

### Accident Risk Model
- **Target:** `accident_risk_level` (4 classes)
- **Features:** Same 23 features plus `congestion_score` and `congestion_level_enc` (25 total)
- **Class balancing:** SMOTE oversampling applied to minority classes
- **Training:** 80/20 split

### Feature engineering
- **Cyclic encoding** — hour and day encoded as sin/cos pairs (e.g. 23:00 is adjacent to 00:00)
- **Speed ratio** — `current_speed / free_flow_speed`, captures deviation from normal flow
- **Label encoding** — categoricals encoded with sklearn LabelEncoder; encoders saved for inference

---

## Setup & Running

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the models

```bash
# On the synthetic dataset (first time / no real data yet):
python train.py

# On real + augmented data:
python train.py --data kochi_traffic_augmented.csv

# Skip plots for faster training:
python train.py --data kochi_traffic_augmented.csv --no-plots
```

Models are saved directly into `models/`.

### 3. Run the dashboard

```bash
streamlit run app.py
```

### 4. Using the dashboard

- Select **Day**, **Hour**, **Weather**, and **Location** from the sidebar
- Click **⚡ ANALYSE TRAFFIC**
- Switch between **Congestion** and **Risk** map tabs
- Click any marker on the map for per-road details
- Use the theme toggle at the top of the sidebar to switch between dark and light mode

---

## Real Data Pipeline

Real traffic data is collected every 30 minutes by a separate collector running on an Android phone via Termux. The collector lives in a separate private repository (`kochi-traffic-data`) and contains:

- `collect.py` — queries TomTom for 57 roads + OpenWeatherMap for weather, derives all 27 columns, appends to CSV, commits and pushes to GitHub
- `run_scheduler.py` — runs `collect()` every 30 minutes inside a GNU Screen session with `termux-wake-lock`
- `status.py` — shows total rows, days collected, weather and congestion breakdowns, and data source split

**APIs used:**
- TomTom Traffic Flow API — current speed, free-flow speed, confidence score per road
- OpenWeatherMap API — rainfall, visibility, temperature, humidity for Kochi city centre

---

## Weather Augmentation

Because the real data was collected during an unusually dry March period (72.9% Cloudy, 26.4% Clear, 0.6% Light Rain, 0% Heavy Rain or Fog), the dataset needs rain and fog rows added before retraining. This is done using `augment_weather.py`:

```bash
python augment_weather.py --real kochi_traffic_real.csv --out kochi_traffic_augmented.csv
```

This generates synthetic Light Rain, Heavy Rain, and Fog rows until each condition reaches at least 8% of the total dataset. Real rows keep `data_source = "real"`, synthetic rows are tagged `data_source = "synthetic"`.

---

## Retraining Workflow

```bash
# 1. Download kochi_traffic_real.csv from the collector GitHub repo
# 2. Augment rain/fog coverage
python augment_weather.py --real kochi_traffic_real.csv --out kochi_traffic_augmented.csv
# 3. Retrain
python train.py --data kochi_traffic_augmented.csv
# 4. Restart dashboard — models/ is already updated
streamlit run app.py
```

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
| Data processing | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| Real data collection | TomTom Traffic Flow API, OpenWeatherMap API |
| Mobile collection | Termux (Android), GNU Screen |
| Data storage | GitHub (private repository) |

---

## Limitations

- **Accident risk is modelled, not recorded** — the system estimates relative risk from traffic and weather inputs. It does not use historical accident records.
- **Weather augmentation** — rain and fog rows in the training data are partially synthetic due to dry collection conditions. This is standard data augmentation practice and is clearly tagged via the `data_source` column.
- **Static inference** — predictions are based on the selected inputs, not a live feed. The dashboard does not auto-refresh.
- **Road coordinates** — major junctions are verified against OpenStreetMap. Smaller local roads are approximate and may be offset by up to 100–200 metres.
