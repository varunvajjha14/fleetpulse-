from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import re
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

def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

@router.get("/")
def list_merchants(db: Session = Depends(get_db)):
    merchants = db.query(Merchant).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone,
            "address": m.address,
            "slug": m.slug
        }
        for m in merchants
    ]

@router.post("/")
def create_merchant(data: MerchantCreate, db: Session = Depends(get_db)):
    existing = db.query(Merchant).filter(Merchant.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate unique slug from name
    base_slug = generate_slug(data.name)
    slug = base_slug
    counter = 1
    while db.query(Merchant).filter(Merchant.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    merchant = Merchant(**data.dict(), slug=slug)
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return {
        "id": merchant.id,
        "message": "Merchant registered",
        "slug": merchant.slug,
        "order_page": f"/order/{merchant.slug}"
    }

@router.get("/slug/{slug}")
def get_merchant_by_slug(slug: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.slug == slug).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {
        "id": merchant.id,
        "name": merchant.name,
        "phone": merchant.phone,
        "address": merchant.address,
        "slug": merchant.slug
    }