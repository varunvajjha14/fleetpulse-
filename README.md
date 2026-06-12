# ⚡ FleetPulse

A B2B SaaS platform enabling local merchants and delivery startups to manage their own hyperlocal rider fleets — without paying aggregator commissions.

Built as a full-stack project covering backend architecture, database design, AI/ML integration, and a modern frontend dashboard.

---

## 🚀 Live Features

- **Merchant Portal** — create delivery orders, track status in real time, view order history
- **Dispatcher Dashboard** — assign riders to orders, manage fleet, update delivery status
- **ACID Transactions** — row-level locking prevents two dispatchers from assigning the same order simultaneously
- **Payout Estimator** — distance-based payout calculation (ML regression model coming in v2)
- **Live Polling** — both portals auto-refresh every 8–10 seconds without page reload

---

## 🛠 Tech Stack

**Backend**
- Python · FastAPI · SQLAlchemy · SQLite
- ACID-compliant transactions with `SELECT FOR UPDATE` row locking
- REST API with auto-generated Swagger docs at `/docs`

**Frontend**
- Vanilla HTML · CSS · JavaScript
- Dark UI with Inter font, custom component system
- Real-time data via polling

**Coming in v2**
- Leaflet.js live rider map
- Chart.js analytics dashboard
- scikit-learn regression model for dynamic payout prediction
- Gemini API review categoriser
- Deployment on Railway + Vercel


## 📁 Project Structure
leetpulse/
├── backend/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLAlchemy engine and session
│   ├── models.py        # DB tables: Merchant, Rider, Order, Trip
│   └── routes/
│       ├── orders.py    # Order CRUD + ACID assign endpoint
│       ├── riders.py    # Rider management
│       └── merchants.py # Merchant registration
└── frontend/
├── index.html       # Landing page
├── merchant.html    # Merchant portal
└── dispatcher.html  # Dispatcher dashboard
# ⚙️ Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/varunvajjha14/fleetpulse-.git
cd fleetpulse-
```

**2. Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
```

**3. Start the server**
```bash
cd backend
uvicorn main:app --reload
```

**4. Open in browser**

| Page | URL |
|------|-----|
| Landing page | http://localhost:8000 |
| Merchant portal | http://localhost:8000/app/merchant.html |
| Dispatcher dashboard | http://localhost:8000/app/dispatcher.html |
| API docs | http://localhost:8000/docs |

---

## 🔐 Key Technical Decisions

**Why row-level locking?**
In a live dispatch environment, two dispatchers could theoretically assign the same order to different riders simultaneously. Using `SELECT FOR UPDATE` inside an explicit database transaction ensures only one assignment can succeed — the second request gets a 400 error with a clear message. This is a real concurrency problem that production logistics platforms solve.

**Why FastAPI over Express?**
The ML layer (coming in v2) is Python-native with scikit-learn. Keeping the entire backend in Python means the payout model runs in the same process as the API — no inter-service HTTP calls needed.

**Why SQLite for now?**
Zero-config for local development. The SQLAlchemy ORM means switching to PostgreSQL for production requires changing exactly one environment variable.

---

## 👤 Author

**Varun Vajjha**  
3rd year IT student · Building FleetPulse as a full-stack portfolio project  
GitHub: [@varunvajjha14](https://github.com/varunvajjha14)

---

## 📌 Project Status

actively in development — v2 features (ML model, live map, deployment) in progress
