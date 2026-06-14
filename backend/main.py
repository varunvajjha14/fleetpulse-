from routes import orders, riders, merchants, reviews

app.include_router(orders.router)
app.include_router(riders.router)
app.include_router(merchants.router)
app.include_router(reviews.router)

# Serve frontend folder — this makes your HTML files available at /app/
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_path = os.path.abspath(frontend_path)
if not os.path.exists(frontend_path):    
    # On Railway, frontend is served separately via Vercel    
    # Skip static file mounting    
    pass
else:    
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Root redirect — visiting localhost:8000 opens index.html automatically
@app.get("/")
def root():    
    if os.path.exists(os.path.join(frontend_path, "index.html")):        
        return FileResponse(os.path.join(frontend_path, "index.html"))    
    return {"message": "FleetPulse API is running", "docs": "/docs"}