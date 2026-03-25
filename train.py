"""
train.py — Kochi Traffic Intelligence Model Trainer
====================================================
Replaces the Google Colab notebook. Trains both XGBoost models locally
and saves all 6 model files directly into the models/ folder.

Usage:
    python train.py                                      # uses kochi_traffic_synthetic_v2.csv
    python train.py --data kochi_traffic_real.csv        # train on real data
    python train.py --data kochi_traffic_augmented.csv   # train on augmented data

Options:
    --data      Path to training CSV (default: kochi_traffic_synthetic_v2.csv)
    --models    Output folder for .pkl files (default: models/)
    --no-plots  Skip saving EDA and confusion matrix charts
"""

import argparse
import os
import pickle
import time

import numpy as np
import pandas as pd

# ── Argument parsing ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train Kochi Traffic ML models")
parser.add_argument("--data",     default="kochi_traffic_synthetic_v2.csv",
                    help="Training CSV file path")
parser.add_argument("--models",   default="models/",
                    help="Output folder for model files")
parser.add_argument("--no-plots", action="store_true",
                    help="Skip EDA and confusion matrix plots")
args = parser.parse_args()

PLOTS = not args.no_plots

# ── Dependency check ──────────────────────────────────────────────────────────
print("\nChecking dependencies...")
missing = []
for pkg in ["xgboost", "sklearn", "imblearn", "matplotlib", "seaborn"]:
    try:
        __import__(pkg if pkg != "sklearn" else "sklearn")
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"\nMissing packages: {', '.join(missing)}")
    print("Run:  pip install xgboost scikit-learn imbalanced-learn matplotlib seaborn")
    exit(1)

from imblearn.over_sampling import SMOTE
from sklearn.metrics import (accuracy_score, classification_report,
                             ConfusionMatrixDisplay)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

if PLOTS:
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use("seaborn-v0_8-whitegrid")

print("All dependencies OK.")

# ── Setup output folder ───────────────────────────────────────────────────────
os.makedirs(args.models, exist_ok=True)
MODELS = args.models.rstrip("/") + "/"

def save(obj, name):
    path = MODELS + name
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  Saved {name:<40} ({size_kb:.1f} KB)")

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'─'*55}")
print(f"  STEP 1 — Loading data")
print(f"{'─'*55}")

if not os.path.exists(args.data):
    print(f"Error: file not found — {args.data}")
    exit(1)

df = pd.read_csv(args.data)
print(f"  File    : {args.data}")
print(f"  Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")

# Show data_source breakdown if mixed
if "data_source" in df.columns:
    src_counts = df["data_source"].value_counts()
    for src, cnt in src_counts.items():
        print(f"  Source  : {src:<12}  {cnt:>6,} rows  ({cnt/len(df)*100:.1f}%)")

print(f"\n  Weather breakdown:")
for w, cnt in df["weather_condition"].value_counts().items():
    bar = "█" * int(cnt / len(df) * 30)
    print(f"    {w:<15} {cnt:>6,}  ({cnt/len(df)*100:.1f}%)  {bar}")

print(f"\n  Congestion breakdown:")
for c, cnt in df["congestion_level"].value_counts().items():
    print(f"    {c:<15} {cnt:>6,}  ({cnt/len(df)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 2. EDA PLOTS (optional)
# ══════════════════════════════════════════════════════════════════════════════
if PLOTS:
    print(f"\n{'─'*55}")
    print(f"  STEP 2 — Generating EDA plots")
    print(f"{'─'*55}")

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("Kochi Traffic Dataset — Overview", fontsize=14, fontweight="bold")

    order  = ["Low", "Moderate", "High", "Very High"]
    colors = ["#00c853", "#ffd600", "#ff6d00", "#d50000"]
    vc     = df["congestion_level"].value_counts().reindex(order).fillna(0)
    axes[0, 0].bar(vc.index, vc.values, color=colors)
    axes[0, 0].set_title("Congestion Level Distribution")

    df["weather_condition"].value_counts().plot(kind="bar", ax=axes[0, 1], color="#1565c0")
    axes[0, 1].set_title("Weather Condition Distribution")
    axes[0, 1].tick_params(axis="x", rotation=30)

    hourly = df.groupby("hour")["congestion_score"].mean()
    axes[0, 2].plot(hourly.index, hourly.values, color="#e53935", linewidth=2,
                    marker="o", markersize=4)
    axes[0, 2].set_title("Avg Congestion Score by Hour")
    axes[0, 2].axvspan(7, 9, alpha=0.15, color="red")
    axes[0, 2].axvspan(17, 20, alpha=0.15, color="red")

    df.groupby("weather_condition")["congestion_score"].mean().sort_values().plot(
        kind="barh", ax=axes[1, 0], color="#0288d1")
    axes[1, 0].set_title("Avg Congestion by Weather")

    axes[1, 1].hist(df["temperature_c"], bins=30, color="#f57c00", edgecolor="white")
    axes[1, 1].set_title("Temperature Distribution (°C)")

    sample = df.sample(min(2000, len(df)), random_state=42)
    axes[1, 2].scatter(sample["rainfall_mm"], sample["congestion_score"],
                       alpha=0.3, color="#6a1b9a", s=10)
    axes[1, 2].set_title("Rainfall vs Congestion Score")

    plt.tight_layout()
    plt.savefig("eda_overview.png", dpi=120, bbox_inches="tight")
    plt.close()
    print("  eda_overview.png saved")
else:
    print(f"\n  STEP 2 — EDA plots skipped (--no-plots)")

# ══════════════════════════════════════════════════════════════════════════════
# 3. PREPROCESSING & FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'─'*55}")
print(f"  STEP 3 — Preprocessing & feature engineering")
print(f"{'─'*55}")

required = ["congestion_score", "current_speed_kmph", "free_flow_speed_kmph",
            "rainfall_mm", "visibility_m", "temperature_c", "humidity_pct"]
before = len(df)
df = df.dropna(subset=required)
dropped = before - len(df)
if dropped:
    print(f"  Dropped {dropped} rows with nulls in key columns")
print(f"  Clean rows: {len(df):,}")

# Cyclic time encoding
DAY_MAP = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
           "Friday": 4, "Saturday": 5, "Sunday": 6}
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
df["day_sin"]  = np.sin(2 * np.pi * df["day_of_week"].map(DAY_MAP) / 7)
df["day_cos"]  = np.cos(2 * np.pi * df["day_of_week"].map(DAY_MAP) / 7)
print("  Cyclic time encoding done (hour_sin/cos, day_sin/cos)")

# Speed ratio
df["speed_ratio"] = (
    df["current_speed_kmph"] / df["free_flow_speed_kmph"].replace(0, 1)
).clip(0, 1.5)
print("  Speed ratio feature done")

# Label encoding
label_encoders = {}
cat_cols = ["area", "road_name", "road_type", "weather_condition",
            "day_of_week", "congestion_level", "accident_risk_level"]
for col in cat_cols:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

save(label_encoders, "label_encoders.pkl")
print("  Label encoders done")

# ══════════════════════════════════════════════════════════════════════════════
# 4. FEATURE DEFINITION
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'─'*55}")
print(f"  STEP 4 — Feature definition")
print(f"{'─'*55}")

FEATURES = [
    "hour", "hour_sin", "hour_cos", "day_sin", "day_cos",
    "is_rush_hour", "is_weekend", "is_night",
    "lanes", "speed_limit_kmph", "road_type_enc",
    "current_speed_kmph", "free_flow_speed_kmph", "speed_ratio",
    "vehicle_volume_est", "congestion_score",
    "weather_condition_enc", "rainfall_mm", "visibility_m",
    "temperature_c", "humidity_pct",
    "area_enc", "road_name_enc",
]

RISK_FEATURES = list(dict.fromkeys(
    FEATURES + ["congestion_score", "congestion_level_enc"]
))

save(FEATURES, "feature_columns.pkl")
save(RISK_FEATURES, "risk_feature_columns.pkl")
print(f"  Congestion features : {len(FEATURES)}")
print(f"  Risk features       : {len(RISK_FEATURES)}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. TRAIN CONGESTION MODEL
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'─'*55}")
print(f"  STEP 5 — Training congestion model")
print(f"{'─'*55}")

X  = df[FEATURES]
y  = df["congestion_level_enc"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f"  Train: {len(X_train):,}   Test: {len(X_test):,}")

cong_model = XGBClassifier(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)

t0 = time.time()
cong_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
elapsed = time.time() - t0

y_pred = cong_model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
print(f"  Training time : {elapsed:.1f}s")
print(f"  Accuracy      : {acc*100:.1f}%")

le_cong  = label_encoders["congestion_level"]
present  = sorted(y_test.unique())
labels_c = le_cong.inverse_transform(present)
print(f"\n  Per-class results:")
report = classification_report(y_test, y_pred, labels=present,
                                target_names=labels_c, output_dict=True)
for cls in labels_c:
    m = report[cls]
    print(f"    {cls:<12}  precision={m['precision']:.2f}  "
          f"recall={m['recall']:.2f}  f1={m['f1-score']:.2f}")

if PLOTS:
    fig, ax = plt.subplots(figsize=(7, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, display_labels=labels_c, ax=ax,
        colorbar=False, cmap="Greens")
    ax.set_title("Congestion Model — Confusion Matrix")
    plt.tight_layout()
    plt.savefig("confusion_congestion.png", dpi=120)
    plt.close()
    print("  confusion_congestion.png saved")

save(cong_model, "congestion_model.pkl")

# ══════════════════════════════════════════════════════════════════════════════
# 6. TRAIN ACCIDENT RISK MODEL
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'─'*55}")
print(f"  STEP 6 — Training accident risk model")
print(f"{'─'*55}")

Xr = df[RISK_FEATURES]
yr = df["accident_risk_level_enc"]

# Drop any classes with fewer than 2 samples
valid = yr.value_counts()[yr.value_counts() >= 2].index
Xr, yr = Xr[yr.isin(valid)], yr[yr.isin(valid)]

Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    Xr, yr, test_size=0.2, random_state=42, stratify=yr)

# SMOTE — balance minority risk classes
k_neighbors = min(3, yr_train.value_counts().min() - 1)
if k_neighbors >= 1:
    sm = SMOTE(random_state=42, k_neighbors=k_neighbors)
    Xr_train, yr_train = sm.fit_resample(Xr_train, yr_train)
    print(f"  After SMOTE: {len(Xr_train):,} training samples")
else:
    print("  SMOTE skipped (too few minority samples)")

print(f"  Train: {len(Xr_train):,}   Test: {len(Xr_test):,}")

risk_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.08,
    subsample=0.85,
    colsample_bytree=0.85,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)

t0 = time.time()
risk_model.fit(Xr_train, yr_train, eval_set=[(Xr_test, yr_test)], verbose=False)
elapsed = time.time() - t0

yr_pred  = risk_model.predict(Xr_test)
acc_r    = accuracy_score(yr_test, yr_pred)
print(f"  Training time : {elapsed:.1f}s")
print(f"  Accuracy      : {acc_r*100:.1f}%")

le_risk  = label_encoders["accident_risk_level"]
present_r  = sorted(yr_test.unique())
labels_r   = le_risk.inverse_transform(present_r)
print(f"\n  Per-class results:")
report_r = classification_report(yr_test, yr_pred, labels=present_r,
                                  target_names=labels_r, output_dict=True)
for cls in labels_r:
    m = report_r[cls]
    print(f"    {cls:<12}  precision={m['precision']:.2f}  "
          f"recall={m['recall']:.2f}  f1={m['f1-score']:.2f}")

if PLOTS:
    fig, ax = plt.subplots(figsize=(7, 5))
    ConfusionMatrixDisplay.from_predictions(
        yr_test, yr_pred, display_labels=labels_r, ax=ax,
        colorbar=False, cmap="Greens")
    ax.set_title("Risk Model — Confusion Matrix")
    plt.tight_layout()
    plt.savefig("confusion_risk.png", dpi=120)
    plt.close()
    print("  confusion_risk.png saved")

save(risk_model, "accident_risk_model.pkl")
save({"congestion_order": ["Low", "Moderate", "High", "Very High"],
      "risk_order":       ["Low", "Moderate", "High", "Very High"]},
     "class_orders.pkl")

# ══════════════════════════════════════════════════════════════════════════════
# 7. FEATURE IMPORTANCE PLOT (optional)
# ══════════════════════════════════════════════════════════════════════════════
if PLOTS:
    print(f"\n{'─'*55}")
    print(f"  STEP 7 — Feature importance plots")
    print(f"{'─'*55}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, model, feats, title in [
        (axes[0], cong_model, FEATURES,      "Congestion Model"),
        (axes[1], risk_model, RISK_FEATURES, "Risk Model"),
    ]:
        imp = pd.Series(model.feature_importances_, index=feats)
        imp.nlargest(15).sort_values().plot(kind="barh", ax=ax, color="#1b5e20")
        ax.set_title(f"{title} — Top 15 Features")
        ax.set_xlabel("Importance Score")

    plt.tight_layout()
    plt.savefig("feature_importance.png", dpi=120)
    plt.close()
    print("  feature_importance.png saved")

# ══════════════════════════════════════════════════════════════════════════════
# 8. SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*55}")
print(f"  TRAINING COMPLETE")
print(f"{'='*55}")
print(f"  Congestion model accuracy : {acc*100:.1f}%")
print(f"  Risk model accuracy       : {acc_r*100:.1f}%")
print(f"\n  Model files saved to: {MODELS}")
for fname in ["congestion_model.pkl", "accident_risk_model.pkl",
              "label_encoders.pkl", "feature_columns.pkl",
              "risk_feature_columns.pkl", "class_orders.pkl"]:
    path = MODELS + fname
    if os.path.exists(path):
        size_kb = os.path.getsize(path) / 1024
        print(f"    {fname:<40} {size_kb:.1f} KB")

print(f"\n  Run the dashboard:  streamlit run app.py")
print(f"{'='*55}\n")
