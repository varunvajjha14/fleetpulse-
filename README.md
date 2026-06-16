# ⚡ FleetPulse

A B2B SaaS platform enabling local merchants and delivery startups to manage their own hyperlocal rider fleets — without paying aggregator commissions.

Built as a full-stack project covering backend architecture, database design, AI/ML integration, and a modern frontend dashboard.

---

## 🌐 Live Demo

| | URL |
|--|--|
| 🖥 App | https://fleetpulse-beta.vercel.app |
| ⚡ API | https://fleetpulse-production-2e5c.up.railway.app |
| 📖 API Docs | https://fleetpulse-production-2e5c.up.railway.app/docs |

---

## ✅ Features

**Authentication**
- JWT-based login system with secure token storage
- Role-based access — Merchant and Dispatcher roles
- Protected routes — token required for all API calls
- Auto-redirect based on role after login

**Merchant Portal**
- Create delivery orders with auto-detect location (GPS + OpenStreetMap geocoding)
- Real-time order tracking with live status updates
- Live activity ticker showing recent order events
- Stats dashboard — active orders, riders online, in transit, delivered

**Dispatcher Dashboard**
- Live dispatch queue with filter tabs (All / Pending / Assigned / In Transit / Delivered)
- Manual rider assignment via modal
- ⚡ Auto-Assign All — FIFO queue assigns all pending orders to available riders instantly
- Leaflet.js live map — rider pins, pickup markers, route lines between pickup and delivery
- Chart.js analytics — orders by status donut, 14-day orders timeline, rider utilization
- AI Review Categoriser — Groq LLaMA 3.1 auto-tags customer feedback into business categories

**Backend**
- FastAPI REST API with auto-generated Swagger docs
- PostgreSQL persistent database (Railway)
- ACID transactions with `SELECT FOR UPDATE` row-level locking
- Performance indexes on status fields and foreign keys
- RandomForest ML payout model trained on 500 synthetic records (R²=0.941)
- Features: distance, time of day, day of week, weather score, peak hours, weekend flag

---

## 🛠 Tech Stack

**Backend**
- Python · FastAPI · SQLAlchemy · PostgreSQL
- ACID-compliant transactions with row-level locking
- JWT authentication with `python-jose` and `passlib`
- REST API with auto-generated Swagger docs at `/docs`

**AI / ML**
- RandomForest regression (scikit-learn) for dynamic payout prediction
- Groq LLaMA 3.1 API for customer review classification
- Synthetic dataset of 500 delivery records for model training

**Frontend**
- Vanilla HTML · CSS · JavaScript
- Leaflet.js + OpenStreetMap for live fleet tracking
- Chart.js for real-time analytics
- Dark UI with Inter font, custom component system
- Auto-geocoding via OpenStreetMap Nominatim (no API key needed)

**DevOps**
- Backend deployed on Railway
- Frontend deployed on Vercel
- PostgreSQL managed database (Railway)
- GitHub Actions ready

---

## 📁 Project Structure
fleetpulse/

├── backend/

│   ├── main.py              # FastAPI app entry point

│   ├── database.py          # SQLAlchemy engine and session

│   ├── models.py            # DB tables: Merchant, Rider, Order, Trip, User

│   ├── seed.py              # Synthetic data seeder (40 orders, 8 riders)

│   ├── routes/

│   │   ├── orders.py        # Order CRUD + ACID assign + auto-assign

│   │   ├── riders.py        # Rider management

│   │   ├── merchants.py     # Merchant registration

│   │   ├── reviews.py       # AI review categorisation (Groq)

│   │   └── auth.py          # JWT login and registration

│   └── ml/

│       ├── generate_and_train.py  # Synthetic data + model training

│       └── predictor.py           # ML inference for payout prediction

└── frontend/

├── index.html           # Landing page

├── login.html           # JWT login + registration

├── merchant.html        # Merchant portal

└── dispatcher.html      # Dispatcher dashboard

---
## ⚙️ Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/varunvajjha14/fleetpulse-.git
cd fleetpulse-
```

**2. Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx groq scikit-learn numpy joblib pandas psycopg2-binary "python-jose[cryptography]" "passlib[bcrypt]"
```

**3. Set up environment variables**

Create `backend/.env`:
DATABASE_URL=sqlite:///./fleetpulse.db

GROQ_API_KEY=your_groq_key_here

SECRET_KEY=your_secret_key_here

**4. Seed the database and train the ML model**
```bash
cd backend
python seed.py
python ml/generate_and_train.py
```

**5. Start the server**
```bash
uvicorn main:app --reload
```

**6. Open in browser**

| Page | URL |
|------|-----|
| Landing page | http://localhost:8000 |
| Login | http://localhost:8000/app/login.html |
| Merchant portal | http://localhost:8000/app/merchant.html |
| Dispatcher dashboard | http://localhost:8000/app/dispatcher.html |
| API docs | http://localhost:8000/docs |

---

## 🔐 Key Technical Decisions

**Why row-level locking?**
In a live dispatch environment, two dispatchers could theoretically assign the same order to different riders simultaneously. Using `SELECT FOR UPDATE` inside an explicit database transaction ensures only one assignment can succeed — the second request gets a 400 error with a clear message. This is a real concurrency problem that production logistics platforms solve.

**Why FastAPI over Express?**
The ML layer is Python-native with scikit-learn. Keeping the entire backend in Python means the payout model runs in the same process as the API — no inter-service HTTP calls needed.

**Why RandomForest over Linear Regression?**
RandomForest captures non-linear relationships between features (e.g. the interaction between peak hours and weather) that linear regression misses. The model achieves R²=0.941 on the test set, explaining 94% of payout variance.

**Why PostgreSQL for production?**
SQLite resets on every Railway redeploy. PostgreSQL persists data permanently. The SQLAlchemy ORM means switching required changing exactly one environment variable — `DATABASE_URL`.

**Why Groq over OpenAI for review classification?**
Groq's free tier has no meaningful rate limits for this use case, and LLaMA 3.1 performs comparably to GPT-3.5 on short text classification tasks. Zero cost for a portfolio project.


---

## 👤 Author

**Varun Vajjha**
3rd year IT student · Building FleetPulse as a full-stack portfolio project
GitHub: [@varunvajjha14](https://github.com/varunvajjha14)

---

## 📌 Project Status

**v1 complete** — authentication, ML payout model, AI review categoriser, live map, analytics, PostgreSQL, deployed on Railway + Vercel

**v2 planned** — WebSocket real-time updates, mobile responsive redesign, rider mobile app
