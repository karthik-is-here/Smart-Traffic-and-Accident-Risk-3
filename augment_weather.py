"""
augment_weather.py — Weather Augmentation for Kochi Traffic Data
================================================================
Use this when your real collected data has very little rain or fog coverage
(e.g. collected during a dry spell). This script generates synthetic rows
for only the missing weather conditions and merges them with your real CSV.

The augmented rows are tagged with data_source = "synthetic" so the model
always knows what it learned from real data vs. generated data.

Usage:
    python augment_weather.py --real kochi_traffic_real.csv --out kochi_traffic_augmented.csv

Options:
    --real      Path to your real collected CSV (required)
    --out       Output path for the merged CSV (default: kochi_traffic_augmented.csv)
    --target    Target % for each rain/fog condition (default: 8)
    --seed      Random seed for reproducibility (default: 42)
"""

import argparse
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# ── Road definitions (must match collect.py exactly) ──────────────────────────
ROADS = [
    {"area": "Edappally", "road_name": "NH 66 Bypass",             "road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    {"area": "Edappally", "road_name": "Edappally Junction",        "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Edappally", "road_name": "Seaport Airport Road",      "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 60},
    {"area": "Edappally", "road_name": "Edappally Toll Junction",   "road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    {"area": "Edappally", "road_name": "Rajagiri Road",             "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Edappally", "road_name": "Edappally North",           "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Edappally", "road_name": "Konthuruthy Road",          "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Edappally", "road_name": "LuLu Mall Access Road",     "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Kakkanad",  "road_name": "Kakkanad Main Road",        "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Kakkanad",  "road_name": "Infopark Expressway",       "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 60},
    {"area": "Kakkanad",  "road_name": "Infopark Road Phase 1",     "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kakkanad",  "road_name": "Infopark Road Phase 2",     "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kakkanad",  "road_name": "Thrippunithura Road",       "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Kakkanad",  "road_name": "CSEZ Road",                 "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kakkanad",  "road_name": "Kolenchery Road",           "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kakkanad",  "road_name": "High Court Road Kakkanad",  "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Fort Kochi","road_name": "Beach Road Fort Kochi",     "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Ridsdale Road",             "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Calvathy Road",             "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Tower Road",                "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Princess Street",           "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Napier Street",             "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Fort Kochi Ferry Road",     "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    {"area": "Fort Kochi","road_name": "Willingdon Island Road",    "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Mattancherry","road_name": "Mattancherry Road",       "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Mattancherry","road_name": "Jew Town Road",           "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    {"area": "Mattancherry","road_name": "Bazaar Road",             "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    {"area": "Mattancherry","road_name": "Pallipuram Road",         "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    {"area": "Mattancherry","road_name": "Dutch Cemetery Road",     "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    {"area": "Mattancherry","road_name": "Thoppumpady Road",        "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Mattancherry","road_name": "Mattancherry Palace Road","road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    {"area": "Mattancherry","road_name": "Harbour Road",            "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Vyttila",  "road_name": "NH 66 Vyttila",             "road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 70},
    {"area": "Vyttila",  "road_name": "Vyttila Junction",          "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Vyttila",  "road_name": "Kundannoor Bridge Road",    "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Vyttila",  "road_name": "Vyttila Mobility Hub Road", "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Vyttila",  "road_name": "Aroor Bypass",              "road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    {"area": "Vyttila",  "road_name": "Chilavannoor Road",         "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Vyttila",  "road_name": "Pachalam Road",             "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Vyttila",  "road_name": "SA Road Vyttila",           "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Palarivattom","road_name": "Palarivattom Junction",  "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Palarivattom","road_name": "NH 85 Palarivattom",    "road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 70},
    {"area": "Palarivattom","road_name": "Kaloor Palarivattom Rd","road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Palarivattom","road_name": "Banerji Road",           "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Palarivattom","road_name": "Vyttila Palarivattom Rd","road_type": "Arterial","lanes": 2, "speed_limit_kmph": 50},
    {"area": "Palarivattom","road_name": "Pullepady Road",         "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Palarivattom","road_name": "Elamkulam Road",         "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kadavanthra","road_name": "Kadavanthra Junction",    "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Kadavanthra","road_name": "MG Road Kadavanthra",     "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Kadavanthra","road_name": "Shanmugham Road",         "road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    {"area": "Kadavanthra","road_name": "Sahodaran Ayyappan Road", "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kadavanthra","road_name": "Ravipuram Road",          "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kadavanthra","road_name": "Chittoor Road",           "road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    {"area": "Kadavanthra","road_name": "Convent Road",            "road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    {"area": "Kadavanthra","road_name": "Judges Avenue",           "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kadavanthra","road_name": "Bristow Road",            "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    {"area": "Kadavanthra","road_name": "Kasturi Ranga Rd",        "road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
]

AREA_MULT = {
    "Edappally": 1.30, "Kakkanad": 1.10, "Fort Kochi": 0.75,
    "Mattancherry": 0.70, "Vyttila": 1.25, "Palarivattom": 1.15, "Kadavanthra": 1.00,
}
CAPACITY = {"Highway": 1800, "Arterial": 1200, "Local": 600}

# ── Weather profiles for rain/fog only ────────────────────────────────────────
RAIN_FOG_PROFILES = {
    "Light Rain":  {"rain": (0.5,  7.5),  "vis": (2000, 5000), "temp": (23, 29), "hum": (78, 90)},
    "Heavy Rain":  {"rain": (7.5, 40.0),  "vis": (500,  2000), "temp": (21, 27), "hum": (88, 99)},
    "Fog":         {"rain": (0.0,  1.0),  "vis": (100,   800), "temp": (22, 27), "hum": (90, 99)},
}

WEATHER_CONG_MULT = {
    "Light Rain": 1.22, "Heavy Rain": 1.45, "Fog": 1.55,
}
WEATHER_RISK_MULT = {
    "Light Rain": 1.4, "Heavy Rain": 1.9, "Fog": 2.2,
}


# ── Helper functions (same logic as generate_dataset.py) ─────────────────────
def hour_factor(hour):
    if   7 <= hour <= 9:   return random.uniform(0.70, 0.95)
    elif 10 <= hour <= 12: return random.uniform(0.40, 0.60)
    elif 13 <= hour <= 14: return random.uniform(0.45, 0.65)
    elif 17 <= hour <= 20: return random.uniform(0.72, 0.98)
    elif 21 <= hour <= 23: return random.uniform(0.20, 0.40)
    elif 0  <= hour <= 5:  return random.uniform(0.05, 0.18)
    else:                  return random.uniform(0.30, 0.50)


def congestion_level(score):
    if score < 0.35: return "Low"
    if score < 0.60: return "Moderate"
    if score < 0.80: return "High"
    return "Very High"


def accident_risk_score(cong, weather, speed, limit, hour):
    risk = cong * 0.35 * WEATHER_RISK_MULT[weather]
    if limit > 0 and (speed / limit) > 1.1:
        risk += 0.15
    if hour >= 22 or hour <= 5:
        risk += 0.10
    return round(max(0.01, min(0.99, risk)), 4)


def risk_level(score):
    if score < 0.25: return "Low"
    if score < 0.50: return "Moderate"
    if score < 0.75: return "High"
    return "Very High"


def make_weather_row(condition, ts, road, day_name, is_weekend):
    """Generate one row for a given weather condition, timestamp, and road."""
    p = RAIN_FOG_PROFILES[condition]
    rain_mm    = round(random.uniform(*p["rain"]), 2)
    vis_m      = int(random.uniform(*p["vis"]))
    temp_c     = round(random.uniform(*p["temp"]), 1)
    hum_pct    = int(random.uniform(*p["hum"]))

    hour       = ts.hour
    minute     = ts.minute
    area_m     = AREA_MULT[road["area"]]
    h_fact     = hour_factor(hour)
    w_fact     = WEATHER_CONG_MULT[condition]
    noise      = random.uniform(0.92, 1.08)

    raw_cong   = h_fact * area_m * w_fact * noise
    if road["road_type"] == "Highway":
        raw_cong *= 0.85
    cong_score = round(max(0.01, min(0.99, raw_cong)), 4)

    free_flow      = float(road["speed_limit_kmph"]) * random.uniform(0.90, 1.05)
    current_speed  = round(free_flow * (1 - cong_score) + random.uniform(-2, 2), 1)
    current_speed  = max(3.0, current_speed)
    free_flow      = round(free_flow, 1)

    capacity   = CAPACITY.get(road["road_type"], 600)
    volume     = int(road["lanes"] * capacity * cong_score * random.uniform(0.9, 1.1))

    a_score    = accident_risk_score(cong_score, condition, current_speed,
                                     road["speed_limit_kmph"], hour)
    is_rush    = 1 if (7 <= hour <= 9 or 17 <= hour <= 20) else 0
    is_night   = 1 if (hour >= 22 or hour <= 5) else 0

    return {
        "timestamp":            ts.strftime("%Y-%m-%d %H:%M:%S"),
        "date":                 ts.strftime("%Y-%m-%d"),
        "day_of_week":          day_name,
        "hour":                 hour,
        "minute":               minute,
        "time_period":          ts.strftime("%H:%M"),
        "area":                 road["area"],
        "road_name":            road["road_name"],
        "road_type":            road["road_type"],
        "lanes":                road["lanes"],
        "speed_limit_kmph":     road["speed_limit_kmph"],
        "weather_condition":    condition,
        "rainfall_mm":          rain_mm,
        "visibility_m":         vis_m,
        "temperature_c":        temp_c,
        "humidity_pct":         hum_pct,
        "current_speed_kmph":   current_speed,
        "free_flow_speed_kmph": free_flow,
        "congestion_score":     cong_score,
        "congestion_level":     congestion_level(cong_score),
        "vehicle_volume_est":   volume,
        "accident_risk_score":  a_score,
        "accident_risk_level":  risk_level(a_score),
        "is_rush_hour":         is_rush,
        "is_weekend":           is_weekend,
        "is_night":             is_night,
        "data_source":          "synthetic",
        "tomtom_confidence":    round(random.uniform(0.75, 1.0), 2),
    }


def generate_rain_fog_rows(real_df, target_pct=8):
    """
    Generate synthetic rain/fog rows so that each weather condition
    reaches at least `target_pct` % of the total combined dataset.

    Timestamps are sampled from the real data's date range so they
    blend naturally with real collection periods.
    """
    total_real  = len(real_df)
    date_range  = pd.to_datetime(real_df["date"].unique())
    min_date    = date_range.min()
    max_date    = date_range.max()

    # Count existing rows per weather condition
    real_counts = real_df["weather_condition"].value_counts().to_dict()

    rows = []

    for condition in ["Light Rain", "Heavy Rain", "Fog"]:
        existing   = real_counts.get(condition, 0)
        # How many rows would we need to hit target_pct of the *final* total?
        # final_total ≈ total_real + all_synthetic_we_add
        # We solve: (existing + n) / (total_real + n_all) >= target_pct/100
        # Approximate: target n so existing+n >= target_pct/100 * total_real
        needed = max(0, int((target_pct / 100) * total_real) - existing)

        if needed == 0:
            print(f"  {condition}: already at target ({existing} rows). Skipping.")
            continue

        print(f"  {condition}: {existing} real rows → adding {needed:,} synthetic rows")

        # Generate random timestamps within the real date range
        day_range = (max_date - min_date).days + 1
        for _ in range(needed):
            rand_day    = min_date + timedelta(days=random.randint(0, day_range - 1))
            rand_hour   = random.randint(0, 23)
            rand_minute = random.choice([0, 30])
            ts          = rand_day.replace(hour=rand_hour, minute=rand_minute,
                                           second=0, microsecond=0)
            day_name    = ts.strftime("%A")
            is_weekend  = 1 if ts.weekday() >= 5 else 0
            road        = random.choice(ROADS)
            rows.append(make_weather_row(condition, ts, road, day_name, is_weekend))

    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Augment real traffic data with rain/fog rows")
    parser.add_argument("--real",   required=True,  help="Path to real collected CSV")
    parser.add_argument("--out",    default="kochi_traffic_augmented.csv",
                                                     help="Output CSV path")
    parser.add_argument("--target", type=int, default=8,
                                                     help="Target %% per rain/fog condition (default: 8)")
    parser.add_argument("--seed",   type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    print(f"\nLoading real data from: {args.real}")
    real_df = pd.read_csv(args.real)
    print(f"Real rows: {len(real_df):,}")
    print(f"\nExisting weather breakdown:")
    for cond, cnt in real_df["weather_condition"].value_counts().items():
        pct = cnt / len(real_df) * 100
        print(f"  {cond:<15} {cnt:>6,}  ({pct:.1f}%)")

    print(f"\nGenerating synthetic rain/fog rows (target: {args.target}% each)...")
    aug_df = generate_rain_fog_rows(real_df, target_pct=args.target)

    if len(aug_df) == 0:
        print("\nNo augmentation needed — all conditions already at target. Saving real data as-is.")
        real_df.to_csv(args.out, index=False)
    else:
        combined = pd.concat([real_df, aug_df], ignore_index=True)
        # Shuffle so synthetic rows aren't all at the end
        combined = combined.sample(frac=1, random_state=args.seed).reset_index(drop=True)
        combined.to_csv(args.out, index=False)

        print(f"\nAugmented dataset saved to: {args.out}")
        print(f"Total rows: {len(combined):,}  "
              f"(real: {len(real_df):,} | synthetic: {len(aug_df):,})")
        print(f"\nFinal weather breakdown:")
        for cond, cnt in combined["weather_condition"].value_counts().items():
            pct = cnt / len(combined) * 100
            src = "real+synth" if cond in ["Light Rain", "Heavy Rain", "Fog"] else "real"
            print(f"  {cond:<15} {cnt:>6,}  ({pct:.1f}%)  [{src}]")

        print(f"\nFinal data_source breakdown:")
        for src, cnt in combined["data_source"].value_counts().items():
            pct = cnt / len(combined) * 100
            print(f"  {src:<12} {cnt:>6,}  ({pct:.1f}%)")

    print(f"\nDone. Upload '{args.out}' to Google Colab to retrain.")


if __name__ == "__main__":
    main()
