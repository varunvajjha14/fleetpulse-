from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
sys.path.append("..")
from database import get_db
from models import Merchant, Order, OrderStatus, Trip

router = APIRouter(prefix="/public", tags=["public"])

class CustomerOrder(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    notes: Optional[str] = None

@router.get("/merchant/{slug}")
def get_merchant_public(slug: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.slug == slug).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {
        "id": merchant.id,
        "name": merchant.name,
        "address": merchant.address,
        "slug": merchant.slug
    }

@router.post("/merchant/{slug}/order")
def place_customer_order(slug: str, data: CustomerOrder, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.slug == slug).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    order = Order(
        merchant_id=merchant.id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        pickup_address=merchant.address or f"{merchant.name} — pickup",
        delivery_address=data.delivery_address,
        delivery_lat=data.delivery_lat,
        delivery_lng=data.delivery_lng,
        notes=data.notes,
        status=OrderStatus.pending
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "tracking_url": f"/track/ORD-{str(order.id).zfill(4)}",
        "merchant_name": merchant.name
    }

@router.get("/track/{order_ref}")
def track_order(order_ref: str, db: Session = Depends(get_db)):
    # Accept both ORD-0001 and raw id formats
    try:
        if order_ref.upper().startswith("ORD-"):
            order_id = int(order_ref[4:])
        else:
            order_id = int(order_ref)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order reference")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    rider_data = None
    if order.trip and order.trip.rider:
        rider = order.trip.rider
        rider_data = {
            "name": rider.name,
            "phone": rider.phone,
            "latitude": rider.latitude,
            "longitude": rider.longitude,
        }

    return {
        "order_id": order.id,
        "order_ref": f"ORD-{str(order.id).zfill(4)}",
        "status": order.status,
        "customer_name": order.customer_name,
        "pickup_address": order.pickup_address,
        "delivery_address": order.delivery_address,
        "pickup_lat": order.pickup_lat,
        "pickup_lng": order.pickup_lng,
        "delivery_lat": order.delivery_lat,
        "delivery_lng": order.delivery_lng,
        "merchant_name": order.merchant.name if order.merchant else None,
        "rider": rider_data,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "assigned_at": order.trip.assigned_at.isoformat() if order.trip and order.trip.assigned_at else None,
    }