import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import config

_cache = {}

def load_models():
    global _cache
    if _cache:
        return _cache
    d = config.MODEL_DIR
    _cache = {
        "cong_model":   pickle.load(open(f"{d}/congestion_model.pkl",    "rb")),
        "risk_model":   pickle.load(open(f"{d}/accident_risk_model.pkl", "rb")),
        "encoders":     pickle.load(open(f"{d}/label_encoders.pkl",      "rb")),
        "features":     pickle.load(open(f"{d}/feature_columns.pkl",     "rb")),
        "risk_features":pickle.load(open(f"{d}/risk_feature_columns.pkl","rb")),
        "class_orders": pickle.load(open(f"{d}/class_orders.pkl",        "rb")),
    }
    return _cache


# Weather defaults (realistic Kochi values per condition)
WEATHER_DEFAULTS = {
    "Clear":       {"rainfall_mm": 0.0,  "visibility_m": 9000, "temperature_c": 32.0, "humidity_pct": 62},
    "Cloudy":      {"rainfall_mm": 0.1,  "visibility_m": 6500, "temperature_c": 29.0, "humidity_pct": 74},
    "Light Rain":  {"rainfall_mm": 3.5,  "visibility_m": 3500, "temperature_c": 26.0, "humidity_pct": 85},
    "Heavy Rain":  {"rainfall_mm": 18.0, "visibility_m": 1000, "temperature_c": 24.0, "humidity_pct": 94},
    "Fog":         {"rainfall_mm": 0.0,  "visibility_m": 400,  "temperature_c": 24.0, "humidity_pct": 96},
}

# Free-flow speed estimates by road type
FREE_FLOW = {"Highway": 75.0, "Arterial": 45.0, "Local": 30.0}

# Congestion estimates by hour and road type (for feature approximation)
HOUR_CONG = {
    "Highway":  [0.08,0.06,0.05,0.05,0.07,0.10,0.22,0.58,0.72,0.40,0.35,0.38,
                 0.42,0.38,0.35,0.38,0.42,0.68,0.80,0.65,0.45,0.30,0.18,0.12],
    "Arterial": [0.10,0.08,0.06,0.06,0.09,0.14,0.32,0.70,0.85,0.52,0.45,0.48,
                 0.54,0.50,0.46,0.50,0.55,0.78,0.90,0.72,0.55,0.38,0.22,0.14],
    "Local":    [0.08,0.06,0.05,0.05,0.07,0.12,0.28,0.62,0.76,0.46,0.40,0.44,
                 0.48,0.44,0.42,0.46,0.50,0.70,0.82,0.65,0.48,0.32,0.18,0.11],
}


def safe_encode(le, value):
    try:
        return int(le.transform([str(value)])[0])
    except:
        return 0


def build_feature_row(area, road_name, day_of_week, hour, weather_condition, models):
    props   = config.ROAD_PROPERTIES.get(road_name, {"road_type":"Arterial","lanes":2,"speed_limit_kmph":50})
    road_type    = props["road_type"]
    lanes        = props["lanes"]
    speed_limit  = props["speed_limit_kmph"]
    weather_vals = WEATHER_DEFAULTS.get(weather_condition, WEATHER_DEFAULTS["Clear"])

    # Estimate congestion score and speed for this hour/road/weather
    base_cong = HOUR_CONG.get(road_type, HOUR_CONG["Arterial"])[hour]
    weather_mult = {"Clear":1.0,"Cloudy":1.08,"Light Rain":1.22,"Heavy Rain":1.45,"Fog":1.55}.get(weather_condition, 1.0)
    cong_score = min(0.99, max(0.01, base_cong * weather_mult))

    free_flow_speed  = FREE_FLOW.get(road_type, 45.0)
    current_speed    = max(3.0, free_flow_speed * (1 - cong_score))
    speed_ratio      = current_speed / free_flow_speed
    capacity         = {"Highway":1800,"Arterial":1200,"Local":600}.get(road_type, 600)
    vehicle_volume   = int(lanes * capacity * cong_score)

    day_num = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(day_of_week)
    is_rush    = 1 if (7 <= hour <= 9 or 17 <= hour <= 20) else 0
    is_weekend = 1 if day_num >= 5 else 0
    is_night   = 1 if (hour >= 22 or hour <= 5) else 0

    enc = models["encoders"]
    row = {
        "hour":                  hour,
        "hour_sin":              np.sin(2 * np.pi * hour / 24),
        "hour_cos":              np.cos(2 * np.pi * hour / 24),
        "day_sin":               np.sin(2 * np.pi * day_num / 7),
        "day_cos":               np.cos(2 * np.pi * day_num / 7),
        "is_rush_hour":          is_rush,
        "is_weekend":            is_weekend,
        "is_night":              is_night,
        "lanes":                 lanes,
        "speed_limit_kmph":      speed_limit,
        "road_type_enc":         safe_encode(enc["road_type"], road_type),
        "current_speed_kmph":    round(current_speed, 1),
        "free_flow_speed_kmph":  free_flow_speed,
        "speed_ratio":           round(speed_ratio, 4),
        "vehicle_volume_est":    vehicle_volume,
        "congestion_score":      round(cong_score, 4),
        "weather_condition_enc": safe_encode(enc["weather_condition"], weather_condition),
        "rainfall_mm":           weather_vals["rainfall_mm"],
        "visibility_m":          weather_vals["visibility_m"],
        "temperature_c":         weather_vals["temperature_c"],
        "humidity_pct":          weather_vals["humidity_pct"],
        "area_enc":              safe_encode(enc["area"], area),
        "road_name_enc":         safe_encode(enc["road_name"], road_name),
    }
    return row
