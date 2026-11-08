from pydantic import BaseModel, Field
from typing import Literal

class Point(BaseModel):
    time: float
    flux: float

class Evidence(BaseModel):
    title: str
    detail: str
    status: Literal["supporting", "caution", "neutral"]

class PredictionResponse(BaseModel):
    target_name: str
    category: str
    confidence: float
    model_name: str
    mode: Literal["trained_model", "demo"]
    summary: str
    features: dict[str, float]
    evidence: list[Evidence]
    points: list[Point]
    disclaimer: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    cnn_available: bool
