from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math, sys
sys.path.append("..")
from database import get_db
from models import Order, OrderStatus, Trip, Rider, RiderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderCreate(BaseModel):
    merchant_id: int
    customer_name: str
    customer_phone: Optional[str] = None
    pickup_address: str
    delivery_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    notes: Optional[str] = None

class AssignOrder(BaseModel):
    rider_id: int

@router.get("/")
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "merchant_name": o.merchant.name if o.merchant else None,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "pickup_address": o.pickup_address,
            "delivery_address": o.delivery_address,
            "status": o.status,
            "notes": o.notes,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "rider_name": o.trip.rider.name if o.trip else None,
            "estimated_payout": o.trip.estimated_payout if o.trip else None,
        }
        for o in orders
    ]

@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = Order(**data.dict())
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"id": order.id, "status": order.status, "message": "Order created"}

@router.post("/{order_id}/assign")
def assign_order(order_id: int, body: AssignOrder, db: Session = Depends(get_db)):
    # Row-level locking: prevents two dispatchers assigning the same order at once
    try:
        order = db.query(Order).filter(Order.id == order_id).with_for_update().first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != OrderStatus.pending:
            raise HTTPException(status_code=400, detail=f"Order is already {order.status}")

        rider = db.query(Rider).filter(Rider.id == body.rider_id).with_for_update().first()
        if not rider:
            raise HTTPException(status_code=404, detail="Rider not found")
        if rider.status != RiderStatus.available:
            raise HTTPException(status_code=400, detail="Rider is not available")

        order.status = OrderStatus.assigned
        rider.status = RiderStatus.busy
        payout = _estimate_payout(order)
        trip = Trip(order_id=order_id, rider_id=body.rider_id, estimated_payout=payout)
        db.add(trip)
        db.commit()
        return {"message": "Assigned successfully", "estimated_payout": payout}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/status")
def update_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = OrderStatus(status)
    if status == "delivered" and order.trip:
        order.trip.delivered_at = datetime.utcnow()
        if order.trip.rider:
            order.trip.rider.status = RiderStatus.available
    db.commit()
    return {"message": f"Status updated to {status}"}

def _estimate_payout(order: Order) -> float:
    if order.pickup_lat and order.delivery_lat:
        dist = math.sqrt((order.pickup_lat - order.delivery_lat)**2 +
                         (order.pickup_lng - order.delivery_lng)**2) * 111
        return round(30 + dist * 8, 2)
    return 50.0