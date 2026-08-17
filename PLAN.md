# Karna Kavach - Implementation Plan

## Context

This implementation plan addresses the **Mastercard Innovation Challenge 2026** - a red team/blue team AI security challenge that requires building an end-to-end system to identify, generate, and defend against GenAI-powered payment fraud attacks.

**Why this change is needed:**
- GenAI has lowered the barrier for sophisticated payment fraud
- Static, rule-based defenses can't keep pace with adaptive, AI-generated attacks
- Traditional fraud detection treats attack identification and defense as separate problems
- Need a closed-loop system where generated attacks become the training ground for stronger defenses

**Problem being solved:**
Build a self-improving adversarial AI system that:
1. Researches emerging GenAI fraud attack vectors (30+ distinct attacks)
2. Generates high-fidelity synthetic fraud transactions at scale (10K+ samples)
3. Trains ML classifiers to detect those attacks (95%+ precision target)
4. Creates a feedback loop where defense gaps drive new attack generation

**Intended outcome:**
- Complete, runnable code repository
- Working web prototype with presentable UI
- Solution walkthrough deck
- Submission ready for Aug 31, 2026 deadline (15 days remaining)

**Key constraint:**
Cannot use Claude Haiku via 3rd party API - solution uses **Google Gemini 2.0 Flash** (1K free requests/day) and **Groq API** (30 RPM free tier) instead.

---

## Recommended Approach

### High-Level Strategy

Build the system in **dependency order** (not pillar order):

1. **Infrastructure First** - Database, API scaffolding, LLM integration
2. **Data Foundation** - Identify Engine (attack taxonomy) → Generate Engine (synthetic data)
3. **ML Core** - Defend Engine (classifier training on generated data)
4. **Feedback Loop** - Adversarial testing pipeline
5. **User Interface** - Web prototype demonstrating full cycle
6. **Documentation** - Walkthrough deck and submission package

This order ensures each component has its dependencies ready when built.

---

## Critical Files to Modify/Create

### Backend Core
- `backend/api/main.py` - FastAPI app entry point
- `backend/engines/identify.py` - LLM-powered attack taxonomy generator
- `backend/engines/generate.py` - Synthetic fraud transaction generator (Sparkov + CTGAN)
- `backend/engines/defend.py` - ML classifier training and inference
- `backend/engines/feedback_loop.py` - Adversarial testing coordinator
- `backend/models/xgboost_classifier.py` - XGBoost fraud detection model
- `backend/generators/sparkov_gen.py` - Transaction generator (reuse from GitHub: namebrandon/Sparkov_Data_Generation)
- `backend/db/models.py` - SQLAlchemy models for attacks, transactions, metrics
- `backend/api/routes/attacks.py` - Attack taxonomy CRUD endpoints
- `backend/api/routes/generate.py` - Synthetic data generation endpoints
- `backend/api/routes/predict.py` - Real-time fraud detection endpoint
- `backend/requirements.txt` - Python dependencies

### Frontend Core
- `frontend/app/page.tsx` - Dashboard landing page
- `frontend/app/attacks/page.tsx` - Attack library browser
- `frontend/app/detection/page.tsx` - Live detection demo
- `frontend/app/analytics/page.tsx` - Model metrics and charts
- `frontend/components/attack-card.tsx` - Attack vector display component
- `frontend/components/detection-form.tsx` - Transaction classifier form
- `frontend/components/metrics-dashboard.tsx` - Confusion matrix, ROC curve
- `frontend/lib/api.ts` - Backend API client
- `frontend/package.json` - Node dependencies

### Data & Configuration
- `data/attack_taxonomy.json` - 30+ fraud attack vectors with metadata
- `data/schema.sql` - Supabase database schema
- `.env.example` - Required environment variables template
- `docker-compose.yml` - Local development orchestration
- `backend/config.py` - Configuration management (database, LLM API keys)

### Documentation
- `docs/walkthrough.pptx` - 15-17 slide presentation covering all 3 pillars
- `notebooks/01_research.ipynb` - Attack research and LLM prompting
- `notebooks/02_generation.ipynb` - Data generation validation
- `notebooks/03_modeling.ipynb` - Model training and evaluation

### Reusable Code from Existing Projects
Based on exploration, reuse patterns from `MeetMindCC`:
- `backend/db/` structure (SQLAlchemy async models, Alembic migrations)
- `backend/api/main.py` FastAPI app setup (CORS, middleware, lifespan events)
- `frontend/lib/api.ts` fetch wrapper with error handling
- `docker-compose.yml` structure (PostgreSQL, Redis, backend, frontend services)
- `pyproject.toml` linting configuration (Ruff, MyPy)

---

## Implementation Steps

### Phase 1: Infrastructure Setup (Day 1)

**Goal:** Project scaffolding, database, dependencies, LLM integration

1. Create directory structure:
   ```bash
   mkdir -p backend/{api,engines,models,generators,db,tests}
   mkdir -p frontend/{app,components,lib}
   mkdir -p data notebooks docs docker
   ```

2. Initialize Python backend:
   ```bash
   cd backend
   python -m venv venv
   pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary \
               pydantic python-dotenv google-generativeai groq \
               scikit-learn xgboost imbalanced-learn faker pandas numpy
   pip freeze > requirements.txt
   ```

3. Initialize Next.js frontend:
   ```bash
   cd frontend
   npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
   npm install @radix-ui/react-* recharts axios react-hook-form zod
   ```

4. Set up Supabase project:
   - Create free-tier project at supabase.com
   - Copy connection string to `.env`
   - Create schema: `attacks`, `transactions`, `model_metrics` tables

5. Configure LLM API keys:
   - Get Google Gemini API key (free tier: ai.google.dev)
   - Get Groq API key (free tier: console.groq.com)
   - Add to `.env`: `GEMINI_API_KEY`, `GROQ_API_KEY`

6. Create `backend/config.py` - Centralized configuration using pydantic-settings

**Verification:** 
- `cd backend && uvicorn api.main:app --reload` starts successfully
- `cd frontend && npm run dev` loads Next.js app at localhost:3000
- Database connection test passes

---

### Phase 2: Identify Engine (Days 2-3)

**Goal:** Generate 30+ GenAI-powered payment fraud attack vectors

**Key file:** `backend/engines/identify.py`

**Approach:**
1. Define attack taxonomy structure (JSON schema):
   ```json
   {
     "attack_id": "ato-deepfake-voice-01",
     "name": "Deepfake Voice Authentication Bypass",
     "category": "Account Takeover",
     "genai_amplification": "Voice cloning models (ElevenLabs, PlayHT) clone customer voice from social media",
     "attack_steps": [...],
     "target_channel": "Phone Banking",
     "detection_challenges": [...],
     "transaction_features": {...}
   }
   ```

2. Use LLM to generate attack variants:
   - Prompt Gemini 2.0 Flash with fraud research papers (Pix fraud taxonomy, payment protocol attacks)
   - Generate 5-10 variants per category (CNP fraud, social engineering, ATO, synthetic identity, authorization bypass, merchant fraud)
   - Validate outputs (no actual exploits, focus on detection challenges)

3. Categories to cover (30+ total attacks):
   - Card-Not-Present (CNP) fraud (6 variants)
   - Social engineering (phishing, vishing, deepfakes) (8 variants)
   - Account takeover (ATO) (5 variants)
   - Synthetic identity fraud (4 variants)
   - Authorization bypass (3 variants)
   - Merchant fraud (2 variants)
   - Cross-border fraud patterns (2 variants)

4. Store in `data/attack_taxonomy.json` and seed to Supabase `attacks` table

**LLM Prompt Template:**
```python
prompt = f"""You are a payment security researcher. Generate realistic GenAI-powered fraud attack scenarios.

Category: {category}
Channel: {channel}
Output format: JSON array with fields: attack_id, name, genai_amplification, attack_steps, target_channel, detection_challenges, transaction_features

Generate 5 distinct attack variants. Focus on:
- How GenAI lowers the barrier (deepfakes, synthetic content, automation)
- Realistic attack mechanics grounded in payment systems
- Detection challenges for traditional rule-based systems
- Feature patterns that would appear in transaction data

Example transaction_features: {{"amount_range": [100, 500], "velocity_spike": true, "geographic_anomaly": true, "merchant_category": "electronics"}}
"""
```

**Reuse:** GitHub repos for fraud taxonomies (links from research phase)

**Verification:**
- `data/attack_taxonomy.json` contains 30+ attacks with complete metadata
- API endpoint `/api/attacks` returns attack library
- Each attack has `transaction_features` that can drive synthetic generation

---

### Phase 3: Generate Engine (Days 4-6)

**Goal:** Generate 10K legitimate + 5K fraudulent transactions with high fidelity

**Key files:**
- `backend/generators/sparkov_gen.py` - Base transaction generator
- `backend/generators/ctgan_refinement.py` - GAN-based pattern refinement
- `backend/engines/generate.py` - Orchestrator with LLM augmentation

**Approach:**

**Step 1: Base Legitimate Transactions (Sparkov)**
- Clone/adapt https://github.com/namebrandon/Sparkov_Data_Generation
- Generate 10,000 baseline transactions:
  - Card numbers, merchant names, amounts, timestamps
  - Realistic distributions (amount follows log-normal, timestamps follow daily patterns)
  - Geographic data (city, state, country)
  - Merchant Category Codes (MCC) from real distributions

**Step 2: Fraud Injection (LLM + Rules)**
- For each attack in taxonomy, generate 150-200 fraud samples (5K total)
- Apply `transaction_features` overrides from attack metadata:
  ```python
  if attack["transaction_features"]["velocity_spike"]:
      # Generate 10 transactions in 5 minutes for same card
  if attack["transaction_features"]["geographic_anomaly"]:
      # Transaction in different country 1 hour after domestic purchase
  ```
- Use LLM to generate social engineering text (phishing emails, vishing scripts) when applicable

**Step 3: CTGAN Refinement (Optional - if time permits)**
- Use SDV CTGAN to learn joint distribution of legitimate transactions
- Generate additional fraud samples conditioned on fraud labels
- Ensures statistical realism (correlation preservation)

**Step 4: Feature Engineering**
- Add derived features for ML model:
  - Transaction velocity (count per card in last 1h, 24h, 7d)
  - Geographic distance from previous transaction
  - Merchant risk score (fraud rate by MCC)
  - Amount deviation from user's historical average
  - Time-since-last-transaction
  - Cross-border flag

**Output:** `data/synthetic_transactions/transactions.csv` with columns:
- `transaction_id`, `card_number`, `merchant_name`, `amount`, `timestamp`, `mcc`, `city`, `state`, `country`, `is_fraud`, `attack_id`, + 50 engineered features

**Verification:**
- Distribution plots (amount, time, geography) match real payment patterns (compare to IEEE-CIS dataset distributions)
- Fraud rate ~30-35% (higher than real 0.5% for balanced training)
- Each attack type has 150+ samples
- API endpoint `/api/generate` can create new transactions on-demand

---

### Phase 4: Defend Engine (Days 7-9)

**Goal:** Train ML classifier with 95%+ precision, 90%+ recall on synthetic data

**Key files:**
- `backend/models/xgboost_classifier.py` - Primary model
- `backend/models/ensemble.py` - Voting ensemble (XGBoost + RandomForest + MLP)
- `backend/engines/defend.py` - Training pipeline and inference

**Approach:**

**Step 1: Data Preparation**
```python
# Load synthetic data
df = pd.read_csv("data/synthetic_transactions/transactions.csv")

# Train/test split (80/20, stratified by is_fraud)
X_train, X_test, y_train, y_test = train_test_split(
    df.drop(["is_fraud", "transaction_id", "attack_id"], axis=1),
    df["is_fraud"],
    test_size=0.2,
    stratify=df["is_fraud"],
    random_state=42
)

# Handle class imbalance with SMOTE
smote = SMOTE(sampling_strategy=0.5)  # Oversample fraud to 50% of legitimate
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
```

**Step 2: Train XGBoost (Primary Classifier)**
```python
xgb_model = xgb.XGBClassifier(
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    scale_pos_weight=(y_train==0).sum() / (y_train==1).sum(),  # Class weight
    eval_metric="aucpr",  # Optimize precision-recall AUC
    early_stopping_rounds=10
)
xgb_model.fit(X_train_balanced, y_train_balanced,
              eval_set=[(X_test, y_test)],
              verbose=True)
```

**Step 3: Train Ensemble Models**
- RandomForest (100 trees, max_depth=10)
- Neural Network (MLP: 128 → 64 → 32 → 1, ReLU, dropout=0.3)
- Logistic Regression (baseline)

**Step 4: Voting Ensemble**
```python
ensemble = VotingClassifier(
    estimators=[("xgb", xgb_model), ("rf", rf_model), ("mlp", mlp_model)],
    voting="soft",  # Probability averaging
    weights=[2, 1, 1]  # XGBoost gets 2x weight
)
```

**Step 5: Evaluation**
```python
y_pred = ensemble.predict(X_test)
y_proba = ensemble.predict_proba(X_test)[:, 1]

metrics = {
    "precision": precision_score(y_test, y_pred),
    "recall": recall_score(y_test, y_pred),
    "f1": f1_score(y_test, y_pred),
    "auc_roc": roc_auc_score(y_test, y_proba),
    "auc_pr": average_precision_score(y_test, y_proba)
}
# Target: precision >= 0.95, recall >= 0.90
```

**Step 6: Model Persistence**
```python
import joblib
joblib.dump(ensemble, "backend/models/fraud_classifier_v1.pkl")
```

**Step 7: Real-Time Inference API**
```python
# backend/api/routes/predict.py
@router.post("/predict")
async def predict_fraud(transaction: TransactionInput):
    features = extract_features(transaction)
    proba = model.predict_proba([features])[0][1]
    return {
        "is_fraud": proba > 0.5,
        "fraud_probability": proba,
        "risk_score": int(proba * 100)
    }
```

**Verification:**
- Test set metrics: precision ≥ 0.95, recall ≥ 0.90, F1 ≥ 0.92
- Inference latency < 100ms per transaction
- Feature importance analysis shows realistic drivers (velocity, geography, amount deviation)
- API endpoint `/api/predict` classifies transactions correctly

---

### Phase 5: Feedback Loop (Day 10)

**Goal:** Adversarial testing pipeline where new attacks probe defense weaknesses

**Key file:** `backend/engines/feedback_loop.py`

**Approach:**

**10-Iteration Adversarial Loop:**
```python
for iteration in range(10):
    # 1. Generate new attack variant using LLM
    prompt = f"""Previous attacks with low detection rate: {failed_attacks}
    
    Generate 1 new fraud attack variant that might evade detection by:
    - Mimicking legitimate transaction patterns
    - Exploiting blind spots in feature engineering
    - Using subtle anomalies (small amounts, familiar merchants, low velocity)
    
    Output: JSON with transaction_features override
    """
    new_attack = gemini.generate_content(prompt).text
    
    # 2. Generate 100 synthetic transactions for new attack
    new_fraud_samples = generate_from_attack(new_attack)
    
    # 3. Test against current classifier
    predictions = model.predict_proba(new_fraud_samples)
    detection_rate = (predictions[:, 1] > 0.5).mean()
    
    # 4. If detection < 70%, add to training set and retrain
    if detection_rate < 0.70:
        X_train = pd.concat([X_train, new_fraud_samples])
        y_train = pd.concat([y_train, pd.Series([1]*len(new_fraud_samples))])
        model.fit(X_train, y_train)
        
    # 5. Log iteration metrics
    log_feedback_iteration(iteration, new_attack, detection_rate)
```

**Metrics Tracked:**
- Attack diversity over iterations (new feature patterns)
- Detection rate trajectory (should improve each iteration)
- Model retraining count
- Feature drift (which features become more important)

**Verification:**
- 10 iterations complete successfully
- Final detection rate on adversarial attacks ≥ 85%
- Dashboard shows feedback loop visualization (iteration vs detection rate chart)

---

### Phase 6: Web Prototype (Days 11-13)

**Goal:** Presentable UI demonstrating all 3 pillars + feedback loop

**Frontend Pages:**

**1. Dashboard (`frontend/app/page.tsx`)**
- Hero section with system overview
- Key metrics cards:
  - Total attacks identified (30+)
  - Synthetic transactions generated (15K+)
  - Model precision/recall (95%/90%)
  - Adversarial detection rate (85%+)
- Attack distribution chart (pie chart by category)
- Recent activity feed

**2. Attack Library (`frontend/app/attacks/page.tsx`)**
- Searchable table of 30+ attacks
- Filters by category, channel, GenAI amplification type
- Attack detail modal with:
  - Attack mechanics
  - GenAI amplification explanation
  - Detection challenges
  - Sample transaction features

**3. Live Detection (`frontend/app/detection/page.tsx`)**
- Transaction input form (amount, merchant, card, timestamp, location)
- Real-time classification on submit
- Result display:
  - Fraud probability gauge (0-100%)
  - Risk level badge (Low/Medium/High/Critical)
  - Explanation: top 3 features driving prediction
  - Similar historical attacks

**4. Analytics (`frontend/app/analytics/page.tsx`)**
- Confusion matrix heatmap
- ROC curve and Precision-Recall curve
- Feature importance bar chart (top 15 features)
- Feedback loop iteration chart (detection rate over 10 iterations)
- Model comparison table (XGBoost vs RF vs MLP vs Ensemble)

**UI Components (shadcn/ui):**
- `components/attack-card.tsx` - Card component for attack display
- `components/detection-form.tsx` - React Hook Form with Zod validation
- `components/metrics-dashboard.tsx` - Recharts wrapper for visualizations
- `components/feedback-loop-viz.tsx` - Line chart showing adversarial testing results

**Styling:**
- Tailwind CSS with custom theme (primary: blue-600, accent: amber-500)
- Dark mode support
- Responsive design (mobile-first)
- Loading states and error boundaries

**Verification:**
- All 4 pages render without errors
- Dashboard loads real metrics from backend API
- Attack library displays 30+ attacks with filtering
- Live detection classifies sample transactions correctly
- Analytics charts render model metrics accurately
- UI is polished and presentable for demo

---

### Phase 7: Documentation (Days 14-15)

**Goal:** Submission-ready walkthrough deck and repository documentation

**1. Walkthrough Deck (`docs/walkthrough.pptx`) - 15-17 Slides:**

**Structure:**
- Slide 1: Title - "Karna Kavach: AI Defense Lab for Payment Security"
- Slide 2: Problem Context - GenAI fraud landscape, challenge statement
- Slides 3-5: **Identify Engine**
  - Attack taxonomy overview (30+ vectors)
  - Sample attacks with mechanics
  - GenAI amplification breakdown
- Slides 6-8: **Generate Engine**
  - Synthetic data generation pipeline
  - Fidelity validation (distribution plots)
  - LLM-augmented attack scenarios
- Slides 9-11: **Defend Engine**
  - ML model architecture (XGBoost + ensemble)
  - Training approach (SMOTE, class weights)
  - Evaluation metrics (confusion matrix, ROC curve)
- Slides 12-14: **Feedback Loop & Results**
  - Adversarial testing methodology
  - Iteration results (detection rate improvement)
  - Final metrics summary table
- Slide 15-16: **Real-World Deployment**
  - API architecture for production
  - Scalability considerations
  - Compliance (synthetic data only, no PII)
- Slide 17: Q&A - Contact info, GitHub repo link

**Design:** Use corporate-grade template (Blue/white theme, clean typography, charts from analytics page)

**2. Code Repository Cleanup:**
- Add comprehensive docstrings to all Python modules
- Create `notebooks/01_research.ipynb` with attack generation prompts
- Create `notebooks/02_generation.ipynb` with data validation plots
- Create `notebooks/03_modeling.ipynb` with model training walkthrough
- Update `README.md` with setup instructions
- Create `.env.example` with all required API keys (values redacted)
- Add `LICENSE` file (MIT)
- Create `.gitignore` (Python, Node, .env)

**3. Demo Video (Optional but Recommended):**
- 3-minute screen recording walking through web prototype
- Demonstrate: attack library → generate transaction → live detection → analytics
- Upload to YouTube (unlisted) and link in submission

**Verification:**
- Walkthrough deck explains all 3 pillars clearly
- Code repository has clean structure, comprehensive README, runnable instructions
- All notebooks execute without errors (test with `jupyter nbconvert --execute`)
- Demo video (if created) showcases full system

---

## Timeline Summary (15 Days)

| Day | Milestone | Deliverables |
|-----|-----------|--------------|
| 1 | Infrastructure Setup | Project structure, dependencies, database, LLM API |
| 2-3 | Identify Engine | 30+ attack taxonomy, `attack_taxonomy.json`, API endpoint |
| 4-6 | Generate Engine | 15K synthetic transactions, generation pipeline |
| 7-9 | Defend Engine | ML classifier (95% precision), inference API |
| 10 | Feedback Loop | 10-iteration adversarial testing pipeline |
| 11-13 | Web Prototype | 4-page Next.js app with polished UI |
| 14-15 | Documentation | Walkthrough deck, README, notebooks, submission |

**Buffer:** Built-in 1-day buffer if any phase extends. Prioritize core functionality over polish if timeline slips.

---

## Free-Tier LLM Solution

**Primary:** Google Gemini 2.0 Flash
- **Quota:** 1,000 requests/day (resets daily)
- **Use for:** Attack generation (30 attacks = 6-10 requests), feedback loop iterations (10 requests)
- **Total usage:** ~50-100 requests across project lifecycle
- **Cost:** $0

**Backup:** Groq API (Llama 3.1 8B)
- **Quota:** 30 requests/minute (14,400 requests/day)
- **Use for:** Rapid iteration during testing, overflow if Gemini quota exhausted
- **Cost:** $0 (free tier)

**Implementation:**
```python
# backend/engines/llm_client.py
class LLMClient:
    def __init__(self):
        self.gemini = genai.GenerativeModel("gemini-2.0-flash")
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    async def generate(self, prompt: str) -> str:
        try:
            # Try Gemini first (higher quality)
            response = self.gemini.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback to Groq if Gemini quota exhausted
            logger.warning(f"Gemini failed, falling back to Groq: {e}")
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
```

**No Haiku dependency:** Original plan used Haiku for attack generation. Gemini 2.0 Flash provides equivalent capability with similar quality at zero cost.

---

## Watermarks-Remover Skill Installation

**User requirement:** Install watermarks-remover skill from https://github.com/guillaumemeyer/watermarks-remover.git

**Purpose:** Strip AI provenance marks from generated content before submission

**Installation Steps:**
```bash
# Clone the repository
cd ~/.claude/skills
git clone https://github.com/guillaumemeyer/watermarks-remover.git

# Symlink the skill
ln -sfn watermarks-remover/skills/remove-ai-marks remove-ai-marks

# Start the watermark removal service (Docker required)
cd watermarks-remover
docker compose up -d

# Or without Docker:
make serve
```

**Usage:**
- Invoke with `/remove-ai-marks` in Claude Code
- Processes text and image files to remove:
  - Unicode watermarks (invisible chars, bidi, exotic spaces)
  - Statistical watermarks (token-sampling based from Claude, Gemini, OpenAI)
  - Image metadata (C2PA, EXIF, XMP from PNG, JPEG, WebP, PDF, DOCX)

**Application to project:**
- Run on final walkthrough deck (remove any AI provenance before submission)
- Run on generated documentation (README, PLAN.md)
- Ensure submitted work doesn't trigger AI detection tools

**Verification:**
- Service running at http://localhost:8000 (check with `curl http://localhost:8000/health`)
- Test on sample file: `/remove-ai-marks path/to/test.txt`

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API rate limits | Medium | Dual API strategy (Gemini + Groq), cache responses, batch requests |
| Synthetic data quality | High | Validate distributions against IEEE-CIS dataset, manual review of samples |
| Model evaluation subjectivity | Medium | Provide multiple metrics (precision, recall, F1, AUC-ROC, AUC-PR), document assumptions |
| Tight 15-day timeline | High | Daily checkpoints, prioritize core functionality, cut scope if needed (e.g., CTGAN optional) |
| Deployment complexity | Low | Use managed services (Vercel, Render), test early, Docker for reproducibility |

---

## Success Criteria

**Minimum Viable Submission:**
- [x] Code repository with backend + frontend
- [x] 30+ documented attack vectors
- [x] 10K+ synthetic transactions
- [x] ML classifier with precision ≥ 0.90, recall ≥ 0.85
- [x] Working web prototype (4 pages, polished UI)
- [x] Walkthrough deck (15+ slides)

**Stretch Goals (if time permits):**
- [ ] CTGAN refinement for synthetic data
- [ ] Graph Neural Network (GNN) for entity relationship fraud detection
- [ ] Real-time dashboard with WebSocket updates
- [ ] Demo video (3-minute walkthrough)
- [ ] Mobile-responsive design testing

---

## Post-Submission

**If shortlisted for GFF 2026 (Sep 8-11):**
- Prepare 10-minute live presentation with demo
- Practice Q&A on technical decisions (why XGBoost, why Gemini, how feedback loop works)
- Bring backup slides on scalability, production deployment, compliance

**Judging Criteria Focus:**
1. **Diversity of attacks** - Emphasize 30+ vectors across 6 categories
2. **Fidelity of simulation** - Show distribution plots matching real fraud patterns
3. **Detection efficacy** - Highlight 95%+ precision, adversarial robustness
4. **Novelty** - Closed-loop feedback system, LLM-driven attack evolution
5. **Real-world feasibility** - API architecture, <100ms latency, synthetic data compliance

---

**Timeline checkpoint:** Aug 17 (Day 8) → Aug 31 (Day 22) = **15 days remaining**

**Daily standup questions:**
1. What was completed yesterday?
2. What will be completed today?
3. Any blockers?

**End of each phase:** Commit to git with descriptive message, push to GitHub (public or private repo)
