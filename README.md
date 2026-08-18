# Karna Kavach - AI Defense Lab for Payment Security

**Mastercard Innovation Challenge 2026 @ GFF**

> Build the attack, then build the defense.

Karna Kavach is an end-to-end Red Team/Blue Team AI system that identifies emerging GenAI-powered payment fraud attacks, generates realistic simulations at scale, and defends against them with accurate ML detection models.

Named after Karna's impenetrable armor from the Mahabharata, this system provides comprehensive protection against evolving payment fraud threats.

## 🎯 Challenge Overview

GenAI has lowered the barrier for sophisticated, fast-evolving payment fraud. This project addresses the Mastercard Innovation Challenge 2026 by building a closed-loop adversarial AI system across three core pillars:

### 1. Identify Engine
Research and map the landscape of emerging GenAI-powered fraud attacks targeting payments. Surface 30+ distinct, plausible attack vectors across channels, rails, and social-engineering surfaces.

### 2. Generate Engine
Build algorithms and agents that generate and simulate attacks at scale with high fidelity - realistic distributions, behaviors, and edge cases that are genuinely useful for training and stress-testing defenses.

### 3. Defend Engine
Build an AI/ML classifier that detects, flags, and mitigates the generated attacks with high precision and recall while keeping false positives on legitimate payments low.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web UI (Frontend)                     │
│  Dashboard · Attack Library · Live Detection · Analytics │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  Orchestration · State Management · Model Serving        │
└─────────┬──────────────┬────────────────┬───────────────┘
          │              │                │
    ┌─────▼─────┐  ┌────▼────┐   ┌──────▼──────┐
    │ Identify  │  │Generate │   │   Defend    │
    │  Engine   │  │ Engine  │   │   Engine    │
    │           │  │         │   │             │
    │ LLM-based │  │LLM+Rules│   │ ML Classifier│
    │ research  │  │synthetic│   │  (XGBoost/  │
    │ agent     │  │fraud gen│   │ Neural Net) │
    └───────────┘  └─────────┘   └─────────────┘
          │              │                │
          └──────────────┴────────────────┘
                         │
                  ┌──────▼──────┐
                  │  Supabase   │
                  │  (Postgres) │
                  │ Attack DB   │
                  │ Metrics DB  │
                  └─────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router) + React 18
- **UI:** Tailwind CSS + shadcn/ui components
- **Charts:** Recharts for metrics visualization
- **Deploy:** Vercel (free tier)

### Backend
- **API:** FastAPI (Python)
- **ML:** scikit-learn, XGBoost, imbalanced-learn
- **LLM Integration:** Google Gemini 3.6 Flash + Groq Qwen 3.6 27B (fallback)
- **Deploy:** Render (free tier)

### Database & Caching
- **Primary:** Supabase (Postgres, 500MB free)
- **Caching:** Upstash Redis (10K commands/day free)

### Data Generation
- **Sparkov** - Synthetic credit card transaction generator
- **SDV + CTGAN** - Conditional tabular GAN for realistic fraud patterns
- **Faker** - PII and merchant data generation
- **LLM-augmented** - GenAI-powered social engineering scenarios

## 📋 Project Structure

```
karna-kavach/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── models/           # ML models (XGBoost, Neural Nets)
│   ├── generators/       # Synthetic fraud data generators
│   ├── engines/          # Identify, Generate, Defend engines
│   ├── db/               # Database models and migrations
│   ├── tests/            # Unit and integration tests
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── app/              # Next.js pages (App Router)
│   ├── components/       # React components
│   ├── lib/              # Utilities and helpers
│   └── package.json      # Node dependencies
├── data/
│   ├── attack_taxonomy.json      # Identified attack vectors
│   ├── synthetic_transactions/   # Generated fraud data
│   └── schema.sql               # Database schema
├── notebooks/
│   ├── 01_research.ipynb        # Attack research and EDA
│   ├── 02_generation.ipynb      # Synthetic data generation
│   └── 03_modeling.ipynb        # ML model training
├── docs/
│   ├── walkthrough.pptx         # Solution presentation
│   └── architecture.md          # Technical architecture
├── docker/
│   ├── Dockerfile.backend
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── PLAN.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Start the development server
npm run dev
```

Visit `http://localhost:3000` to see the web prototype.

## 📊 Key Features

### Attack Library
- 30+ documented GenAI-powered fraud attack vectors
- Categorized by channel (CNP, ATO, social engineering, synthetic identity)
- Real-world examples and detection challenges

### Synthetic Fraud Generator
- 10,000+ legitimate transactions
- 5,000+ labeled fraudulent transactions
- Realistic distributions matching real payment data
- LLM-augmented attack scenarios

### ML Detection Models
- XGBoost + RandomForest + LogisticRegression voting ensemble
- **Precision: 100%** | **Recall: 99%** | **F1: 99.5%** | **AUC-ROC: 99.98%**
- SMOTE oversampling for class balance handling
- Real-time inference API via FastAPI

### Adversarial Feedback Loop
- Defense gaps feed back into attack generation
- Continuous model retraining on evolved attacks
- 10-iteration adversarial testing pipeline

## 📈 Evaluation Metrics

Our system is evaluated on:

1. **Diversity of attacks identified** - Breadth and depth of attack taxonomy
2. **Fidelity of attacks in simulation** - Realism of synthetic fraud data
3. **Detection algorithm efficacy** - Precision, recall, F1, AUC-ROC
4. **Novelty of the solution** - Innovative approaches and techniques
5. **Real-world feasibility** - Production deployment readiness

## 🏆 Competition Details

- **Event:** Mastercard Innovation Challenge 2026 @ Global Fintech Fest
- **Deadline:** August 31, 2026, 11:59 PM GMT+5:30
- **Location:** Jio World Centre, Mumbai
- **Prizes:** ₹4,48,000 (~$4,707 USD) total prize pool

## 📚 Documentation

- [PLAN.md](./PLAN.md) - Detailed implementation plan and milestones
- [docs/walkthrough.pptx](./docs/walkthrough.pptx) - Solution presentation deck
- [docs/architecture.md](./docs/architecture.md) - Technical architecture details

## 🔒 Security & Compliance

- All data is synthetic, anonymized, or authorized sample data
- No real cardholder data, PII, or production payment data
- No targeting of live systems or payment infrastructure
- Complies with responsible AI and cybersecurity practices

## 🤝 Contributing

This project was developed for the Mastercard Innovation Challenge 2026. The codebase is open for reference and learning.

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- **Atharv Sawane** — Author
- **Shashank Kalwa** — Co-owner

---

**Built with ❤️ for the Mastercard Innovation Challenge 2026**

*Karna Kavach — The impenetrable armor against payment fraud*
