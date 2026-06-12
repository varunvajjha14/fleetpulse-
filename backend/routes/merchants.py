from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.append("..")
from database import get_db
from models import Merchant

router = APIRouter(prefix="/merchants", tags=["merchants"])

class MerchantCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

@router.get("/")
def list_merchants(db: Session = Depends(get_db)):
    merchants = db.query(Merchant).all()
    return [{"id": m.id, "name": m.name, "email": m.email, "phone": m.phone} for m in merchants]

@router.post("/")
def create_merchant(data: MerchantCreate, db: Session = Depends(get_db)):
    existing = db.query(Merchant).filter(Merchant.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    merchant = Merchant(**data.dict())
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return {"id": merchant.id, "message": "Merchant registered"}