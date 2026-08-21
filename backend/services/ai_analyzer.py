def analyze_incident(description: str):
    text = description.lower()

    disaster_type = "Unknown"
    severity = "Low"
    priority = "Normal"
    confidence = 0.60

    if any(word in text for word in ["flood", "flooding", "water"]):
        disaster_type = "Flood"
        confidence = 0.90

    elif any(word in text for word in ["earthquake", "tremor", "shaking"]):
        disaster_type = "Earthquake"
        confidence = 0.90

    elif any(word in text for word in ["fire", "burning", "flames"]):
        disaster_type = "Fire"
        confidence = 0.90

    elif any(word in text for word in ["landslide", "land slide"]):
        disaster_type = "Landslide"
        confidence = 0.90

    if any(word in text for word in [
        "dead", "death", "trapped", "critical", "collapsed"
    ]):
        severity = "Critical"
        priority = "Immediate"

    elif any(word in text for word in [
        "injured", "severe", "major", "destroyed"
    ]):
        severity = "High"
        priority = "High"

    elif any(word in text for word in [
        "damage", "affected", "heavy"
    ]):
        severity = "Medium"
        priority = "Medium"

    return {
        "disaster_type": disaster_type,
        "severity": severity,
        "priority": priority,
        "confidence": confidence
    }