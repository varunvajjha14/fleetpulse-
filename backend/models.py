from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"

class RiderStatus(str, enum.Enum):
    available = "available"
    busy = "busy"
    offline = "offline"

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders = relationship("Order", back_populates="merchant")

class Rider(Base):
    __tablename__ = "riders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    status = Column(Enum(RiderStatus), default=RiderStatus.available, index=True)
    latitude = Column(Float, default=19.0760)
    longitude = Column(Float, default=72.8777)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trips = relationship("Trip", back_populates="rider")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String)
    pickup_address = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False)
    pickup_lat = Column(Float)
    pickup_lng = Column(Float)
    delivery_lat = Column(Float)
    delivery_lng = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    merchant = relationship("Merchant", back_populates="orders")
    trip = relationship("Trip", back_populates="order", uselist=False)

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    rider_id = Column(Integer, ForeignKey("riders.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    estimated_payout = Column(Float, default=0.0)
    order = relationship("Order", back_populates="trip")
    rider = relationship("Rider", back_populates="trips")

class UserRole(str, enum.Enum):
    merchant = "merchant"
    dispatcher = "dispatcher"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())