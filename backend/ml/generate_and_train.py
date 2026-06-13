import numpy as np
import pandas as pd
import joblib
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

np.random.seed(42)
N = 500

print("Generating synthetic delivery dataset...")

# ── Features ──
distance_km     = np.random.uniform(1, 25, N)
hour_of_day     = np.random.randint(0, 24, N)
day_of_week     = np.random.randint(0, 7, N)   # 0=Mon, 6=Sun
weather_score   = np.random.uniform(0, 1, N)   # 0=clear, 1=heavy rain

# ── Business logic baked into the synthetic data ──
# Peak hours: 8-10am, 12-2pm, 6-9pm → higher payout
is_peak = ((hour_of_day >= 8)  & (hour_of_day <= 10) |
           (hour_of_day >= 12) & (hour_of_day <= 14) |
           (hour_of_day >= 18) & (hour_of_day <= 21)).astype(float)

# Weekend surcharge
is_weekend = (day_of_week >= 5).astype(float)

# Base payout formula with noise
base_payout = (
    25                              # base
    + distance_km * 4              # distance factor (reduced)
    + is_peak * 35                 # peak hour bonus (increased)
    + is_weekend * 25              # weekend bonus (increased)
    + weather_score * 40           # weather surcharge (increased)
    + np.random.normal(0, 8, N)   # more real-world noise
)

# Clip to realistic range
payout = np.clip(base_payout, 20, 250)

# ── Build DataFrame ──
df = pd.DataFrame({
    'distance_km':   distance_km,
    'hour_of_day':   hour_of_day,
    'day_of_week':   day_of_week,
    'weather_score': weather_score,
    'is_peak':       is_peak,
    'is_weekend':    is_weekend,
    'payout':        payout
})

print(f"Dataset shape: {df.shape}")
print(f"Payout range: ₹{payout.min():.1f} — ₹{payout.max():.1f}")
print(f"Average payout: ₹{payout.mean():.1f}")

# ── Train/test split ──
X = df[['distance_km', 'hour_of_day', 'day_of_week', 'weather_score', 'is_peak', 'is_weekend']]
y = df['payout']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)} samples")

# ── Train RandomForest ──
print("Training RandomForest model...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ── Evaluate ──
y_pred = model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)
r2     = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"  MAE (Mean Absolute Error): ₹{mae:.2f}")
print(f"  R² Score: {r2:.3f}  (1.0 = perfect, >0.85 = good)")

# ── Feature importance ──
print(f"\nFeature Importance:")
features = X.columns.tolist()
for feat, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
    bar = '█' * int(imp * 40)
    print(f"  {feat:<20} {bar} {imp:.3f}")

# ── Save model ──
model_dir  = os.path.dirname(__file__)
model_path = os.path.join(model_dir, 'payout_model.pkl')
joblib.dump(model, model_path)
print(f"\n✅ Model saved to {model_path}")
print("Run your FastAPI server — ML predictions are now live!")