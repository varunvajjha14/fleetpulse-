import joblib
import os
import math
import numpy as np
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'payout_model.pkl')
_model = None

def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run: python backend/ml/generate_and_train.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model

def _distance_km(lat1, lng1, lat2, lng2) -> float:
    # Haversine formula — real geographic distance
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lng/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

def _weather_score() -> float:
    # Simulated weather — in Week 3 replace with live OpenWeatherMap API
    # Returns 0.0 (clear) to 1.0 (heavy rain)
    hour = datetime.utcnow().hour
    # Simulate slightly worse weather in evening
    if 15 <= hour <= 20:
        return np.random.uniform(0.3, 0.7)
    return np.random.uniform(0.0, 0.3)

def predict_payout(
    pickup_lat: float,
    pickup_lng: float,
    delivery_lat: float,
    delivery_lng: float,
    created_at: datetime = None
) -> float:
    """
    Predict rider payout using trained RandomForest model.
    Falls back to distance formula if model not available.
    """
    try:
        model = _load_model()
        now   = created_at or datetime.utcnow()

        distance    = _distance_km(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        hour        = now.hour
        day         = now.weekday()
        weather     = _weather_score()
        is_peak     = 1.0 if (8<=hour<=10 or 12<=hour<=14 or 18<=hour<=21) else 0.0
        is_weekend  = 1.0 if day >= 5 else 0.0

        features = np.array([[distance, hour, day, weather, is_peak, is_weekend]])
        payout   = model.predict(features)[0]

        return round(float(np.clip(payout, 20, 250)), 2)

    except FileNotFoundError:
        # Fallback to simple formula if model missing
        if pickup_lat and delivery_lat:
            dist = math.sqrt((pickup_lat-delivery_lat)**2 +
                           (pickup_lng-delivery_lng)**2) * 111
            return round(30 + dist * 8, 2)
        return 50.0
    except Exception as e:
        print(f"ML prediction error: {e}")
        return 50.0