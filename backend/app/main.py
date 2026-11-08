from pathlib import Path
import io
import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .demo import make_demo_curve
from .features import extract_features, clean_lightcurve
from .explain import build_evidence
from .predictor import ModelService

app = FastAPI(
    title="ASTRA Exoplanet Finder API",
    description="Light-curve analysis and exoplanet transit signal classification.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
service = ModelService()
DISCLAIMER = "A model classification is not a confirmed exoplanet discovery. Independent validation and follow-up observations are required."

@app.get("/")
def root():
    return {"name": "ASTRA Exoplanet Finder API", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "model_loaded": service.loaded,
        "model_name": service.model_name,
        "cnn_available": service.cnn_available
    }

@app.get("/api/demo")
def demo():
    time, flux = make_demo_curve()
    features = extract_features(time, flux)
    # Fixed illustrative output so the demo never masquerades as a trained inference.
    category = "Planet candidate"
    summary, evidence = build_evidence(features, category)
    return {
        "target_name": "DEMO-KIC-001",
        "category": category,
        "confidence": 0.94,
        "model_name": "Simulated demonstration",
        "mode": "demo",
        "summary": "This is a simulated example designed to demonstrate the interface. No trained model was run.",
        "features": features,
        "evidence": evidence,
        "points": [{"time": float(t), "flux": float(f)} for t, f in zip(time, flux)],
        "disclaimer": "Simulated demonstration only. This is not NASA data and not a real model prediction."
    }

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a CSV file.")
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(413, "File exceeds the 15 MB upload limit.")
        frame = pd.read_csv(io.BytesIO(content))
        lower = {c.lower().strip(): c for c in frame.columns}
        if "time" not in lower or "flux" not in lower:
            raise HTTPException(400, "CSV must contain columns named 'time' and 'flux'.")
        time = pd.to_numeric(frame[lower["time"]], errors="coerce").to_numpy()
        flux = pd.to_numeric(frame[lower["flux"]], errors="coerce").to_numpy()
        time, flux = clean_lightcurve(time, flux)
        result = service.predict(time, flux)
        return result
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except Exception as exc:
        raise HTTPException(400, f"Could not analyse this light curve: {exc}")

@app.get("/api/model/metrics")
def model_metrics():
    path = Path(__file__).resolve().parents[1] / "reports" / "baseline_metrics.json"
    if not path.exists():
        return {"available": False, "message": "Train and evaluate a model to populate metrics."}
    return {"available": True, **__import__("json").loads(path.read_text())}
