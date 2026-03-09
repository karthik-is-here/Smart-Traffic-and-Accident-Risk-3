import pandas as pd
import numpy as np
import config
from data_utils import load_models, build_feature_row


def predict_all_roads(area, day_of_week, hour, weather_condition):
    models = load_models()
    roads  = config.AREA_ROADS.get(area, [])
    enc    = models["encoders"]
    co     = models["class_orders"]

    cong_order = co["congestion_order"]
    risk_order = co["risk_order"]

    results = []
    for road_name in roads:
        try:
            row = build_feature_row(area, road_name, day_of_week, hour, weather_condition, models)

            # ── Congestion prediction ──────────────────────────────────────────
            feat_df = pd.DataFrame([{k: row[k] for k in models["features"] if k in row}])
            c_enc   = int(models["cong_model"].predict(feat_df)[0])
            c_prob  = float(models["cong_model"].predict_proba(feat_df).max())
            c_classes = list(models["cong_model"].classes_)
            try:
                c_label = enc["congestion_level"].inverse_transform([c_enc])[0]
            except:
                c_label = cong_order[min(c_enc, len(cong_order)-1)]
            c_score = round(row["congestion_score"] * 100, 1)

            # ── Risk prediction ────────────────────────────────────────────────
            risk_row = dict(row)
            risk_row["congestion_score"]      = row["congestion_score"]
            risk_row["congestion_level_enc"]  = c_enc
            rfeat_df = pd.DataFrame([{k: risk_row[k] for k in models["risk_features"] if k in risk_row}])
            r_enc    = int(models["risk_model"].predict(rfeat_df)[0])
            try:
                r_label = enc["accident_risk_level"].inverse_transform([r_enc])[0]
            except:
                r_label = risk_order[min(r_enc, len(risk_order)-1)]

            # Compute risk score from congestion + weather
            weather_mult = {"Clear":1.0,"Cloudy":1.1,"Light Rain":1.4,"Heavy Rain":1.9,"Fog":2.2}.get(weather_condition, 1.0)
            r_score = round(min(99.0, row["congestion_score"] * 35 * weather_mult), 1)

            props = config.ROAD_PROPERTIES.get(road_name, {})
            lat, lon = config.ROAD_COORDINATES.get(road_name, (9.9975, 76.2900))

            peak_time = "07:00–09:00 / 17:00–20:00" if props.get("road_type") in ["Highway","Arterial"] else "08:00–09:00"

            results.append({
                "road_name":           road_name,
                "congestion_level":    c_label,
                "congestion_score":    c_score,
                "accident_risk_level": r_label,
                "accident_risk_score": r_score,
                "lat":                 lat,
                "lon":                 lon,
                "road_type":           props.get("road_type", "Arterial"),
                "speed_limit_kmph":    props.get("speed_limit_kmph", 50),
                "lanes":               props.get("lanes", 2),
                "current_speed_kmph":  row["current_speed_kmph"],
                "temperature_c":       row["temperature_c"],
                "rainfall_mm":         row["rainfall_mm"],
                "visibility_m":        row["visibility_m"],
                "humidity_pct":        row["humidity_pct"],
                "peak_time":           peak_time,
                "weather_condition":   weather_condition,
            })
        except Exception as e:
            continue

    return results
