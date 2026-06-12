from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.append("..")
from database import get_db
from models import Rider, RiderStatus

router = APIRouter(prefix="/riders", tags=["riders"])

class RiderCreate(BaseModel):
    name: str
    phone: str
    latitude: Optional[float] = 19.0760
    longitude: Optional[float] = 72.8777

@router.get("/")
def list_riders(db: Session = Depends(get_db)):
    riders = db.query(Rider).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "phone": r.phone,
            "status": r.status,
            "latitude": r.latitude,
            "longitude": r.longitude,
        }
        for r in riders
    ]

@router.post("/")
def create_rider(data: RiderCreate, db: Session = Depends(get_db)):
    rider = Rider(**data.dict())
    db.add(rider)
    db.commit()
    db.refresh(rider)
    return {"id": rider.id, "message": "Rider added"}

@router.patch("/{rider_id}/status")
def update_status(rider_id: int, status: str, db: Session = Depends(get_db)):
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    rider.status = RiderStatus(status)
    db.commit()
    return {"message": f"Rider status set to {status}"}