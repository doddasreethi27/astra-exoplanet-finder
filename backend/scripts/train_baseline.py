"""Train a Random Forest baseline using target-level train/test separation."""
import argparse, json
from pathlib import Path
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.features import extract_features, FEATURE_NAMES

BASE = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/processed/lightcurves.csv")
    args = parser.parse_args()
    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = BASE / data_path
    frame = pd.read_csv(data_path, dtype={"target_id": str})
    required = {"target_id", "time", "flux", "label"}
    if not required.issubset(frame.columns):
        raise SystemExit(f"Dataset must contain {sorted(required)}")
    samples, labels, groups = [], [], []
    for target, group in frame.groupby("target_id"):
        label_values = group["label"].dropna().astype(str).str.upper().unique()
        if len(label_values) != 1 or label_values[0] not in {"PC", "FP"}:
            continue
        try:
            features = extract_features(group["time"], group["flux"])
        except Exception as exc:
            print(f"Skipping {target}: {exc}")
            continue
        samples.append([features[name] for name in FEATURE_NAMES])
        labels.append(label_values[0])
        groups.append(target)
    if len(samples) < 10 or len(set(labels)) < 2:
        raise SystemExit("Need at least 10 usable targets and both PC and FP labels.")
    X, y, groups = np.asarray(samples), np.asarray(labels), np.asarray(groups)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    model = RandomForestClassifier(
        n_estimators=400, max_depth=8, min_samples_leaf=2,
        class_weight="balanced", random_state=42, n_jobs=-1
    )
    model.fit(X[train_idx], y[train_idx])
    pred = model.predict(X[test_idx])
    precision, recall, f1, _ = precision_recall_fscore_support(
        y[test_idx], pred, labels=["PC", "FP"], average="macro", zero_division=0
    )
    metrics = {
        "available": True,
        "model": "Random Forest",
        "target_count": int(len(y)),
        "train_targets": int(len(train_idx)),
        "test_targets": int(len(test_idx)),
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "labels": ["PC", "FP"],
        "confusion_matrix": confusion_matrix(y[test_idx], pred, labels=["PC", "FP"]).tolist(),
        "classification_report": classification_report(y[test_idx], pred, labels=["PC", "FP"], output_dict=True, zero_division=0),
        "feature_importance": dict(zip(FEATURE_NAMES, map(float, model.feature_importances_))),
        "note": "Held-out split is grouped by target_id. Metrics are only meaningful if labels and targets are curated without leakage."
    }
    (BASE / "models").mkdir(exist_ok=True)
    (BASE / "reports").mkdir(exist_ok=True)
    joblib.dump(model, BASE / "models" / "random_forest.joblib")
    (BASE / "models" / "feature_names.json").write_text(json.dumps(FEATURE_NAMES, indent=2))
    (BASE / "reports" / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k:v for k,v in metrics.items() if k not in {"classification_report","feature_importance"}}, indent=2))

if __name__ == "__main__":
    main()
