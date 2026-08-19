# Karna Kavach — AI Defense Lab for Payment Security

> Build the attack, then build the defense.

Karna Kavach is a **Red Team / Blue Team AI system** for payment fraud defense. It identifies emerging GenAI-powered fraud attack vectors, generates realistic synthetic fraud data at scale, and trains ML models to detect them — all within a closed-loop adversarial feedback pipeline.

Named after [Karna's impenetrable armor](https://en.wikipedia.org/wiki/Karna) from the Mahabharata, the system provides comprehensive, self-improving protection against evolving payment fraud threats.

---

## How It Works

The system runs a three-phase pipeline:

```
┌──────────────────────────────────────────────────────────────┐
│                    Web Dashboard (Next.js)                    │
│  Attack Library · Live Detection · Analytics · Simulations   │
└──────────────────┬───────────────────────────────────────────┘
                   │ REST API
┌──────────────────▼───────────────────────────────────────────┐
│               Backend API (FastAPI + Python)                  │
│   Orchestration · Model Serving · Real-Time Inference         │
└────────┬───────────────┬────────────────┬────────────────────┘
         │               │                │
   ┌─────▼─────┐   ┌────▼────┐    ┌─────▼──────┐
   │ Identify  │   │Generate │    │  Defend    │
   │  Engine   │   │ Engine  │    │  Engine    │
   │           │   │         │    │            │
   │ LLM-based │   │Faker +  │    │ XGBoost + │
   │ attack    │   │LLM-aug. │    │ RF + LR   │
   │ research  │   │synthetic│    │ Ensemble  │
   │           │   │fraud gen│    │ Classifier│
   └─────┬─────┘   └────┬────┘    └─────┬─────┘
         │              │               │
         └──────────────┴───────────────┘
                        │
            ┌───────────▼───────────┐
            │  Adversarial Feedback │
            │  Loop (10 iterations) │
            │  Attack → Detect →    │
            │  Retrain → Repeat     │
            └───────────────────────┘
```

### Phase 1: Identify

An LLM-powered research agent (Google Gemini / Groq) maps the landscape of GenAI-powered fraud attacks. It produces a structured **attack taxonomy** of 30+ distinct attack vectors, categorized across:

- **Account Takeover** — Deepfake voice/video auth bypass, credential stuffing
- **Card-Not-Present Fraud** — AI-generated merchant facades, tokenization exploits
- **Synthetic Identity Fraud** — LLM-assembled identities, credit-building schemes
- **Social Engineering** — AI chatbot phishing, vishing with voice cloning
- **Authorization Bypass** — Real-time OTP interception, biometric spoofing
- **Merchant & Refund Fraud** — AI-forged receipts, coordinated refund abuse

Each attack includes: GenAI amplification details, step-by-step methodology, target channels, detection challenges, and expected transaction features.

### Phase 2: Generate

The Generate Engine creates **15,000+ synthetic transactions** (10K legitimate + 5K fraud) with realistic distributions:

- **Faker** for PII, merchant names, and geographic data
- **Feature engineering**: velocity tracking, amount deviation, cross-border signals
- **Attack-injected fraud**: each taxonomy attack generates ~150 fraud transactions with attack-specific behavioral signatures (velocity spikes, geographic anomalies, amount ranges)
- **10% international legitimate transactions** to prevent geographic feature leakage

### Phase 3: Defend

A **soft-voting ensemble classifier** (XGBoost + Random Forest + Logistic Regression) trained on 8 engineered features:

| Feature | Description |
|---|---|
| `amount` | Transaction amount |
| `velocity_1h` | Transactions by this card in the last hour |
| `amount_deviation` | How far from the cardholder's average spend |
| `cross_border` | Whether the transaction crosses country borders |
| `card_present` | Physical card present at POS |
| `txn_index` | Sequential index per cardholder |
| `mcc` | Merchant Category Code |
| `merchant_category_enc` | Label-encoded merchant category |

**Current model performance:**

| Metric | Score |
|---|---|
| Precision | 99.89% |
| Recall | 98.61% |
| F1-Score | 99.25% |
| AUC-ROC | 99.98% |
| AUC-PR | 99.96% |

### Adversarial Feedback Loop

After initial training, an automated loop runs 10 iterations:

1. Ask the LLM to design a new **evasive** attack variant
2. Generate 100 probe transactions using that attack
3. Test the current model's detection rate
4. If detection < 70%, inject the new attack into the taxonomy, regenerate data, and **retrain**
5. Log iteration results and move to the next round

This ensures the system continuously hardens itself against novel attack patterns.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 (App Router), React 18, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | FastAPI (Python 3.10+), async with uvicorn |
| **ML** | scikit-learn, XGBoost, imbalanced-learn (SMOTE), pandas, numpy |
| **LLM** | Google Gemini 3.6 Flash (primary), Groq (fallback) |
| **Data** | Faker, custom synthetic generators |
| **Database** | PostgreSQL (prod), SQLite via aiosqlite (local fallback) |
| **Deploy** | Docker Compose (Postgres + Backend + Frontend) |

---

## Project Structure

```
karna-kavach/
├── backend/
│   ├── api/                         # FastAPI app + route handlers
│   │   ├── main.py                  # App entry point, lifespan, CORS
│   │   └── routes/
│   │       ├── attacks.py           # GET /api/attacks/, categories, by-id
│   │       ├── predict.py           # POST /api/predict/, train, metrics
│   │       └── generate.py          # POST /api/generate/transaction, batch
│   ├── engines/
│   │   ├── identify.py              # LLM attack taxonomy research
│   │   ├── generate.py              # Synthetic fraud data generator
│   │   ├── defend.py                # ML ensemble + adversarial loop
│   │   └── llm_client.py            # Gemini / Groq abstraction
│   ├── db/
│   │   ├── database.py              # Async SQLAlchemy engine + session
│   │   └── models.py                # ORM models (Attack, Transaction, Metric)
│   ├── models/                      # Persisted ML artifacts
│   │   ├── fraud_classifier_v1.pkl  # Trained ensemble model
│   │   ├── label_encoder_v1.pkl     # Persisted LabelEncoder
│   │   └── metrics.json             # Latest training metrics
│   ├── pipeline.py                  # CLI: run full identify→generate→defend
│   ├── retrain.py                   # Quick retrain script
│   ├── config.py                    # Settings (env vars, API keys)
│   ├── requirements.txt             # Python dependencies
│   └── tests/                       # pytest test suite
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Dashboard home page
│   │   ├── attacks/page.tsx         # Attack taxonomy browser
│   │   ├── detection/page.tsx       # Live fraud detection UI
│   │   └── analytics/page.tsx       # Model metrics & charts
│   ├── components/                  # Reusable React components
│   ├── lib/api.ts                   # Shared API client
│   ├── next.config.js               # Next.js config (standalone output)
│   └── package.json
├── data/
│   ├── attack_taxonomy.json         # 31 identified attack vectors
│   ├── synthetic_transactions/
│   │   └── transactions.csv         # Generated dataset (~15K rows)
│   └── schema.sql                   # PostgreSQL schema
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml               # Full-stack orchestration
├── notebooks/                       # Jupyter EDA & modeling notebooks
├── docs/                            # Architecture docs & presentation
├── .env.example                     # Environment variable template
└── PLAN.md                          # Implementation plan & milestones
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your API keys (GEMINI_API_KEY, GROQ_API_KEY)

# Start the API server
uvicorn api.main:app --reload
```

The backend starts at `http://localhost:8000`. Without PostgreSQL, it automatically falls back to SQLite + JSON-based data serving.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to see the dashboard.

### Docker (full stack with PostgreSQL)

```bash
docker-compose up --build
```

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend together.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/attacks/` | List all attack vectors (with optional `?category=` filter) |
| `GET` | `/api/attacks/categories/list` | List attack categories |
| `GET` | `/api/attacks/{attack_id}` | Get a single attack by ID |
| `POST` | `/api/predict/` | Predict fraud probability for a transaction |
| `GET` | `/api/predict/metrics` | Get current model performance metrics |
| `POST` | `/api/predict/train` | Trigger model retraining (background) |
| `POST` | `/api/predict/feedback-loop` | Run adversarial feedback loop |
| `POST` | `/api/generate/transaction` | Generate a single synthetic transaction |
| `POST` | `/api/generate/batch` | Generate a batch of transactions |

### Example: Fraud Prediction

```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Unknown Electronics",
    "merchant_category": "electronics",
    "amount": 4999.99,
    "city": "Lagos",
    "country": "NG",
    "card_present": false,
    "velocity_1h": 8,
    "amount_deviation": 15.0,
    "cross_border": true,
    "mcc": 5732,
    "txn_index": 50
  }'
```

Response:

```json
{
  "is_fraud": true,
  "fraud_probability": 0.935,
  "risk_score": 93,
  "confidence": "high",
  "top_features": {
    "amount_deviation": 15.0,
    "cross_border": 1,
    "velocity_1h": 8
  }
}
```

---

## Security & Data Ethics

- **All data is synthetic** — no real cardholder data, PII, or production payment data is used
- Fraud attack research is for **defensive purposes only**
- No live systems or payment infrastructure are targeted
- Complies with responsible AI and cybersecurity research practices

---

## Team

- **Atharv Sawane** — Author
- **Shashank Kalwa** — Co-owner

---

## License

MIT License — See [LICENSE](./LICENSE) for details.

---

*Karna Kavach — The impenetrable armor against payment fraud*
