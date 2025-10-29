#!/usr/bin/env python3
"""Generate small demo ML artifacts for local testing.

This script creates a `backend/models` directory (if missing) and writes a set of
minimal sklearn models, scalers and encoders matching filenames expected by the
project's comprehensive model tests.

Run from repository root:
    python backend/scripts/generate_demo_models.py
"""
import os
from pathlib import Path
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, LabelEncoder


MODELS_DIR = Path(__file__).resolve().parents[1] / "models"


def ensure_models_dir():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def save(obj, name):
    path = MODELS_DIR / name
    joblib.dump(obj, path)
    print(f"Wrote: {path}")


def make_regressor_with_scaler(feature_columns):
    # tiny dataset
    X = np.array([[14, 1, 5, 1, 0], [9, 2, 2, 0, 0], [18, 5, 10, 1, 0]])
    y = np.array([12.0, 8.0, 20.0])
    scaler = StandardScaler()
    scaler.fit(X[:, : len(feature_columns)])
    model = LinearRegression()
    model.fit(scaler.transform(X[:, : len(feature_columns)]), y)
    return {"model": model, "scaler": scaler, "feature_columns": feature_columns}


def make_triage_model(feature_columns):
    X = np.array([[1, 0, 1, 14, 1], [0, 1, 0, 9, 2], [0, 0, 1, 18, 5]])
    y = np.array([2, 1, 3])
    scaler = StandardScaler()
    scaler.fit(X[:, : len(feature_columns)])
    clf = DecisionTreeClassifier()
    clf.fit(scaler.transform(X[:, : len(feature_columns)]), y)
    return {"model": clf, "scaler": scaler, "feature_columns": feature_columns}


def make_anomaly_model():
    X = np.random.RandomState(0).randn(100, 5)
    iso = IsolationForest(random_state=0)
    iso.fit(X)
    return {"model": iso}


def make_peak_model(feature_columns):
    X = np.array([[14, 1, 12, 0, 25], [9, 2, 6, 0, 10], [18, 5, 11, 0, 30]])
    y = np.array([0.7, 0.2, 0.9])
    scaler = StandardScaler()
    scaler.fit(X[:, : len(feature_columns)])
    model = RandomForestRegressor(n_estimators=5, random_state=0)
    model.fit(scaler.transform(X[:, : len(feature_columns)]), y)
    return {"model": model, "scaler": scaler, "feature_columns": feature_columns}


def main():
    ensure_models_dir()

    # Wait time models
    wait_features = ["hour", "day_of_week", "queue_length", "is_peak_hour", "is_weekend"]
    for name in [
        "wait_time_model.pkl",
        "practical_wait_time_model.pkl",
        "advanced_wait_time_model.pkl",
        "optimized_wait_time_model.pkl",
        "ensemble_wait_time_model.pkl",
    ]:
        save(make_regressor_with_scaler(wait_features), name)

    # Triage models
    triage_features = ["age_group_Adult", "insurance_type_Private", "department_Emergency", "hour", "day_of_week"]
    for name in ["triage_priority_model.pkl", "optimized_triage_model.pkl", "ensemble_triage_model.pkl"]:
        save(make_triage_model(triage_features), name)

    # Anomaly models (use IsolationForest placeholder for all anomaly slots)
    for name in ["anomaly_isolation_forest.pkl", "anomaly_dbscan.pkl", "anomaly_lof.pkl", "anomaly_one_class_svm.pkl"]:
        save(make_anomaly_model(), name)

    # Peak time models
    peak_features = ["hour", "day_of_week", "month", "is_weekend", "current_patients"]
    for name in ["peak_time_model.pkl", "optimized_peak_time_model.pkl", "peak_time_gradient_boosting.pkl", "peak_time_random_forest.pkl"]:
        save(make_peak_model(peak_features), name)

    # Encoders
    dept = LabelEncoder()
    dept.fit(["Emergency", "Cardiology", "General"])
    save(dept, "department_encoder.pkl")

    age = LabelEncoder()
    age.fit(["Child", "Adult", "Senior"])
    save(age, "age_encoder.pkl")

    ins = LabelEncoder()
    ins.fit(["Private", "Public", "None"])
    save(ins, "insurance_encoder.pkl")

    triage_enc = LabelEncoder()
    triage_enc.fit(["Low", "Medium", "High"])
    save(triage_enc, "triage_encoder.pkl")

    # Scalers (names expected by tests)
    wt_scaler = StandardScaler()
    wt_scaler.fit([[14, 1, 5], [9, 2, 2], [18, 5, 10]])
    save(wt_scaler, "wait_time_scaler.pkl")

    triage_scaler = StandardScaler()
    triage_scaler.fit([[1, 0, 1], [0, 1, 0], [0, 0, 1]])
    save(triage_scaler, "triage_scaler.pkl")

    peak_scaler = StandardScaler()
    peak_scaler.fit([[14, 1, 12], [9, 2, 6], [18, 5, 11]])
    save(peak_scaler, "peak_time_scaler.pkl")

    print("\nDemo models generation complete.")


if __name__ == "__main__":
    main()
