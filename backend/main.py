from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from routes import orders, riders, merchants
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FleetPulse API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(riders.router)
app.include_router(merchants.router)

# Serve frontend folder — this makes your HTML files available at /app/
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_path = os.path.abspath(frontend_path)
app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Root redirect — visiting localhost:8000 opens index.html automatically
@app.get("/")
def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))