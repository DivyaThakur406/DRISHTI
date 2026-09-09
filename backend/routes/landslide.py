from fastapi import APIRouter
from pydantic import BaseModel

from ..ml.ml_predictor import predict_landslide_risk

router = APIRouter(
    prefix="/risk",
    tags=["Landslide Risk"]
)

class LandslideRiskInput(BaseModel):
    rainfall: float
    soil_moisture: float
    slope: float
    elevation: float
    vegetation_loss: float
    terrain_instability: float

@router.post("/predict")
def predict_landslide_risk_api(data: LandslideRiskInput):
    return predict_landslide_risk(
        data.rainfall,
        data.soil_moisture,
        data.slope,
        data.elevation,
        data.vegetation_loss,
        data.terrain_instability
    )
