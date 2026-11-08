
from pathlib import Path
import joblib
import numpy as np
from .features import extract_features, FEATURE_NAMES, resample_sequence
from .explain import build_evidence

BASE = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE / "models" / "random_forest.joblib"
CNN_PATH = BASE / "models" / "exoplanet_cnn.keras"

class ModelService:
    def __init__(self):
        self.model = None
        self.cnn_model = None
        self.model_name = "Not trained"
        self._load()

    def _load(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            self.model_name = "Random Forest baseline"
        if CNN_PATH.exists():
            try:
                import tensorflow as tf
                self.cnn_model = tf.keras.models.load_model(CNN_PATH)
                if self.model is None:
                    self.model_name = "1D CNN"
            except Exception as exc:
                print(f"Could not load optional CNN model: {exc}")

    @property
    def loaded(self):
        return self.model is not None or self.cnn_model is not None

    @property
    def cnn_available(self):
        return self.cnn_model is not None

    def predict(self, time, flux):
        features = extract_features(time, flux)
        if self.model is not None:
            row = np.array([[features[name] for name in FEATURE_NAMES]], dtype=float)
            probabilities = self.model.predict_proba(row)[0]
            classes = list(self.model.classes_)
            idx = int(np.argmax(probabilities))
            raw_label = str(classes[idx])
            confidence = float(probabilities[idx])
            model_name = "Random Forest baseline"
        elif self.cnn_model is not None:
            sequence = resample_sequence(time, flux)[np.newaxis, ..., np.newaxis]
            probability_pc = float(self.cnn_model.predict(sequence, verbose=0).ravel()[0])
            raw_label = "PC" if probability_pc >= 0.5 else "FP"
            confidence = probability_pc if raw_label == "PC" else 1 - probability_pc
            model_name = "1D CNN"
        else:
            raise RuntimeError(
                "No trained model is installed. Train the baseline with "
                "backend/scripts/train_baseline.py or the CNN with "
                "backend/scripts/train_cnn.py, or use Demo Analysis."
            )
        category = "Planet candidate" if raw_label == "PC" else "False positive"
        summary, evidence = build_evidence(features, category)
        return {
            "target_name": "Uploaded light curve",
            "category": category,
            "confidence": confidence,
            "model_name": model_name,
            "mode": "trained_model",
            "summary": summary,
            "features": features,
            "evidence": evidence,
            "points": [{"time": float(t), "flux": float(f)} for t, f in zip(time, flux)],
            "disclaimer": "Model output is a research aid, not an astronomical confirmation. Labels reflect the training catalogue and may contain selection biases."
        }
