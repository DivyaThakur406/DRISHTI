def calculate_landslide_risk(
    rainfall,
    soil_moisture,
    slope,
    elevation,
    vegetation_loss,
    terrain_instability
):
    rainfall_score = min(max(rainfall, 0), 100)
    soil_score = min(max(soil_moisture, 0), 100)
    slope_score = min(max(slope, 0), 100)
    elevation_score = min(max(elevation, 0), 100)
    vegetation_score = min(max(vegetation_loss, 0), 100)
    terrain_score = min(max(terrain_instability, 0), 100)

    risk = (
        rainfall_score * 0.30 +
        soil_score * 0.20 +
        slope_score * 0.20 +
        elevation_score * 0.10 +
        vegetation_score * 0.10 +
        terrain_score * 0.10
    )

    risk = round(min(max(risk, 0), 100), 2)

    if risk >= 80:
        level = "CRITICAL"
        warning = True
    elif risk >= 60:
        level = "HIGH"
        warning = True
    elif risk >= 40:
        level = "MODERATE"
        warning = False
    else:
        level = "LOW"
        warning = False

    return {
        "risk_score": risk,
        "risk_level": level,
        "early_warning": warning
    }