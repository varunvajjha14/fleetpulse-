import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import engine, SessionLocal, Base
from models import Merchant, Rider, Order, Trip, OrderStatus, RiderStatus
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Clear existing data ──
print("Clearing existing data...")
db.query(Trip).delete()
db.query(Order).delete()
db.query(Rider).delete()
db.query(Merchant).delete()
db.commit()

# ── Merchants ──
merchants = [
    Merchant(name="Chai Point",        email="chai@fleetpulse.com",    phone="9876501001", address="Andheri West, Mumbai"),
    Merchant(name="Box8",              email="box8@fleetpulse.com",    phone="9876501002", address="Bandra East, Mumbai"),
    Merchant(name="Swiggy Dark Store", email="swiggy@fleetpulse.com",  phone="9876501003", address="Powai, Mumbai"),
    Merchant(name="Zepto Mumbai",      email="zepto@fleetpulse.com",   phone="9876501004", address="Juhu, Mumbai"),
]
db.add_all(merchants)
db.commit()
print(f"✅ {len(merchants)} merchants created")

# ── Riders ──
rider_data = [
    ("Rahul Sharma",   "9820001001", 19.0760, 72.8777),
    ("Amit Patil",     "9820001002", 19.0596, 72.8295),
    ("Suresh Yadav",   "9820001003", 19.0544, 72.9005),
    ("Vikram Singh",   "9820001004", 19.1136, 72.8697),
    ("Deepak More",    "9820001005", 19.0330, 72.8650),
    ("Rajan Gupta",    "9820001006", 19.0728, 72.8826),
    ("Nikhil Desai",   "9820001007", 19.0459, 72.8881),
    ("Karan Mehta",    "9820001008", 19.1197, 72.9051),
]
riders = []
for name, phone, lat, lng in rider_data:
    r = Rider(name=name, phone=phone, latitude=lat, longitude=lng, status=RiderStatus.available)
    db.add(r)
    riders.append(r)
db.commit()
print(f"✅ {len(riders)} riders created")

# ── Mumbai pickup/delivery locations ──
locations = [
    ("Andheri West",  19.0596, 72.8295),
    ("Bandra East",   19.0544, 72.9005),
    ("Powai",         19.1136, 72.9050),
    ("Juhu",          19.1075, 72.8263),
    ("Kurla",         19.0728, 72.8826),
    ("Dadar",         19.0178, 72.8478),
    ("Worli",         19.0130, 72.8152),
    ("Goregaon",      19.1663, 72.8526),
    ("Malad",         19.1874, 72.8484),
    ("Borivali",      19.2307, 72.8567),
    ("Thane",         19.2183, 72.9781),
    ("Navi Mumbai",   19.0330, 73.0297),
    ("Chembur",       19.0522, 72.9005),
    ("Mulund",        19.1726, 72.9560),
    ("Vikhroli",      19.1075, 72.9263),
]

customers = [
    ("Priya Nair", "9900001001"),
    ("Rohit Shah", "9900001002"),
    ("Sneha Joshi", "9900001003"),
    ("Arjun Kapoor", "9900001004"),
    ("Divya Menon", "9900001005"),
    ("Aakash Verma", "9900001006"),
    ("Pooja Iyer", "9900001007"),
    ("Manish Tiwari", "9900001008"),
    ("Kavya Reddy", "9900001009"),
    ("Siddharth Rao", "9900001010"),
    ("Ananya Singh", "9900001011"),
    ("Tarun Bhat", "9900001012"),
]

import math

def estimate_payout(plat, plng, dlat, dlng):
    dist = math.sqrt((plat - dlat)**2 + (plng - dlng)**2) * 111
    return round(30 + dist * 8, 2)

# ── Orders — spread over last 14 days ──
statuses = [
    OrderStatus.delivered,
    OrderStatus.delivered,
    OrderStatus.delivered,
    OrderStatus.delivered,
    OrderStatus.in_transit,
    OrderStatus.assigned,
    OrderStatus.pending,
    OrderStatus.pending,
]

orders_created = []
now = datetime.utcnow()

print("Creating orders...")
for i in range(40):
    merchant  = random.choice(merchants)
    customer  = random.choice(customers)
    pickup    = random.choice(locations)
    delivery  = random.choice([l for l in locations if l != pickup])
    status    = random.choice(statuses)
    days_ago  = random.randint(0, 13)
    hours_ago = random.randint(0, 23)
    created   = now - timedelta(days=days_ago, hours=hours_ago)

    order = Order(
        merchant_id=merchant.id,
        customer_name=customer[0],
        customer_phone=customer[1],
        pickup_address=f"{pickup[0]}, Mumbai",
        delivery_address=f"{delivery[0]}, Mumbai",
        pickup_lat=pickup[1],
        pickup_lng=pickup[2],
        delivery_lat=delivery[1],
        delivery_lng=delivery[2],
        status=status,
        created_at=created,
    )
    db.add(order)
    db.flush()

    # For non-pending orders assign a rider and create a trip
    if status != OrderStatus.pending:
        rider = random.choice(riders)
        payout = estimate_payout(pickup[1], pickup[2], delivery[1], delivery[2])
        trip = Trip(
            order_id=order.id,
            rider_id=rider.id,
            estimated_payout=payout,
            assigned_at=created + timedelta(minutes=random.randint(2, 10)),
            delivered_at=created + timedelta(minutes=random.randint(20, 60)) if status == OrderStatus.delivered else None,
        )
        db.add(trip)

    orders_created.append(order)

db.commit()
print(f"✅ {len(orders_created)} orders created")

# ── Set some riders as busy ──
for rider in random.sample(riders, 3):
    rider.status = RiderStatus.busy
db.commit()

db.close()
print("\n🚀 Database seeded successfully!")
print(f"   {len(merchants)} merchants | {len(riders)} riders | {len(orders_created)} orders")
print("   Restart your server and open the dashboard")