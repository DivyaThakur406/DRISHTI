import joblib
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "landslide_model.pkl"
model = joblib.load(MODEL_PATH)

FEATURES = [
    "rainfall",
    "soil_moisture",
    "slope",
    "elevation",
    "vegetation_loss",
    "terrain_instability"
]

CLASS_SCORE = {
    "LOW": 20,
    "MODERATE": 50,
    "HIGH": 70,
    "CRITICAL": 90
}

def predict_landslide_risk(
    rainfall,
    soil_moisture,
    slope,
    elevation,
    vegetation_loss,
    terrain_instability
):
    values = [[
        rainfall,
        soil_moisture,
        slope,
        elevation,
        vegetation_loss,
        terrain_instability
    ]]

    data = pd.DataFrame(values, columns=FEATURES)

    predicted_level = model.predict(data)[0]
    probabilities = model.predict_proba(data)[0]

    class_probabilities = dict(
        zip(model.classes_, probabilities)
    )

    # Continuous prototype score from model class probabilities.
    risk_score = sum(
        class_probabilities.get(level, 0) * score
        for level, score in CLASS_SCORE.items()
    )

    confidence = max(probabilities) * 100

    return {
        "risk_score": round(float(risk_score), 2),
        "risk_level": predicted_level,
        "confidence": round(float(confidence), 2),
        "early_warning": predicted_level in ["HIGH", "CRITICAL"]
    }
