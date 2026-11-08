"""Optional 1D CNN training on per-target fixed-length flux sequences."""
import argparse, json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.features import resample_sequence

BASE = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/processed/lightcurves.csv")
    parser.add_argument("--epochs", type=int, default=35)
    args = parser.parse_args()
    try:
        import tensorflow as tf
    except ImportError:
        raise SystemExit("Install optional dependencies: pip install -r requirements-cnn.txt")
    path = Path(args.data)
    if not path.is_absolute():
        path = BASE / path
    frame = pd.read_csv(path, dtype={"target_id": str})
    X, y, groups = [], [], []
    for target, group in frame.groupby("target_id"):
        labels = group["label"].dropna().astype(str).str.upper().unique()
        if len(labels) != 1 or labels[0] not in {"PC", "FP"}:
            continue
        try:
            X.append(resample_sequence(group["time"], group["flux"]))
            y.append(1 if labels[0] == "PC" else 0)
            groups.append(target)
        except Exception as exc:
            print(f"Skipping {target}: {exc}")
    X = np.asarray(X)[..., np.newaxis]
    y, groups = np.asarray(y), np.asarray(groups)
    if len(y) < 20 or len(np.unique(y)) < 2:
        raise SystemExit("Need at least 20 usable targets and both PC and FP classes.")
    train_idx, test_idx = next(GroupShuffleSplit(test_size=.25, random_state=42).split(X, y, groups))
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1024, 1)),
        tf.keras.layers.Conv1D(32, 9, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(64, 7, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(96, 5, activation="relu", padding="same"),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dropout(.35),
        tf.keras.layers.Dense(48, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
    model.fit(X[train_idx], y[train_idx], validation_split=.2, epochs=args.epochs, batch_size=16,
              callbacks=[tf.keras.callbacks.EarlyStopping(patience=6, restore_best_weights=True)], verbose=1)
    probabilities = model.predict(X[test_idx]).ravel()
    predictions = (probabilities >= .5).astype(int)
    report = classification_report(y[test_idx], predictions, output_dict=True, zero_division=0)
    (BASE / "models").mkdir(exist_ok=True)
    (BASE / "reports").mkdir(exist_ok=True)
    model.save(BASE / "models" / "exoplanet_cnn.keras")
    (BASE / "reports" / "cnn_metrics.json").write_text(json.dumps({
        "target_count": len(y), "test_targets": len(test_idx),
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y[test_idx], predictions).tolist(),
        "note": "Target-level split. Small datasets can produce unstable metrics."
    }, indent=2))
    print("Saved CNN and reports.")

if __name__ == "__main__":
    main()
