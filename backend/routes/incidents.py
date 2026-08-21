from ..services.ai_analyzer import analyze_incident
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Incident
from ..schemas import IncidentCreate, IncidentResponse

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    new_incident = Incident(**incident.model_dump())

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident
@router.post("/{incident_id}/analyze")
def analyze_incident_api(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    result = analyze_incident(incident.description)

    incident.disaster_type = result["disaster_type"]
    incident.severity = result["severity"]

    db.commit()
    db.refresh(incident)

    return {
        "incident_id": incident.id,
        "analysis": result
    }
@router.post("/analyze/{incident_id}")
def analyze(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = analyze_incident(incident.description)

    return result