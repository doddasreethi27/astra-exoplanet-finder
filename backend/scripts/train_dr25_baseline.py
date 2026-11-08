
"""Train a Random Forest using the Kepler DR25 KOI catalogue."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parents[1]

INPUT = BASE / "data" / "processed" / "dr25_training_data.csv"

FEATURES = [
    "koi_period",
    "koi_depth",
    "koi_duration",
    "koi_model_snr",
]


def main():
    df = pd.read_csv(INPUT)

    X = df[FEATURES]
    y = df["target"].astype(int)
    groups = df["kepid"]

    # Keep all records from the same target star together.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=42,
    )

    train_idx, test_idx = next(
        splitter.split(X, y, groups)
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=400,
            max_depth=8,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_test,
            predictions,
            labels=[0, 1],
            average="macro",
            zero_division=0,
        )
    )

    metrics = {
        "available": True,
        "model": "DR25 Random Forest",
        "dataset": "Kepler Q1-Q17 DR25 KOI",
        "feature_names": FEATURES,
        "total_records": int(len(df)),
        "train_records": int(len(train_idx)),
        "test_records": int(len(test_idx)),
        "train_unique_stars": int(groups.iloc[train_idx].nunique()),
        "test_unique_stars": int(groups.iloc[test_idx].nunique()),
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "labels": ["FALSE POSITIVE", "PLANET-LIKE"],
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=[0, 1]
        ).tolist(),
        "classification_report": classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["FALSE POSITIVE", "PLANET-LIKE"],
            output_dict=True,
            zero_division=0,
        ),
        "feature_importance": dict(zip(
            FEATURES,
            map(
                float,
                model.named_steps[
                    "classifier"
                ].feature_importances_,
            ),
        )),
        "note": (
            "Catalogue-based baseline using DR25 KOI features. "
            "Split grouped by target star. This is not raw "
            "light-curve detection or independent planet confirmation."
        ),
    }

    models_dir = BASE / "models"
    reports_dir = BASE / "reports"

    models_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    # Separate artifact: do not overwrite the light-curve model.
    joblib.dump(
        model,
        models_dir / "dr25_catalog_random_forest.joblib",
    )

    (reports_dir / "dr25_baseline_metrics.json").write_text(
        json.dumps(metrics, indent=2)
    )

    print("\nDR25 RANDOM FOREST RESULTS")
    print("--------------------------")
    print(json.dumps({
        k: v for k, v in metrics.items()
        if k not in {
            "classification_report",
            "feature_importance",
        }
    }, indent=2))

    print("\nCLASSIFICATION REPORT:")
    print(classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["FALSE POSITIVE", "PLANET-LIKE"],
        zero_division=0,
    ))

    print("\nFEATURE IMPORTANCE:")
    for name, importance in metrics["feature_importance"].items():
        print(f"{name}: {importance:.4f}")

    print("\nSaved model and evaluation report.")


if __name__ == "__main__":
    main()
