# SupplyGuard AI — Agentic Supplier Risk Intelligence

End-to-end assignment Capstone Implementation: synthetic data + deterministic risk engine + LangGraph + supplier-scoped RAG + optional OpenAI LLM + FastAPI + Streamlit.

## Key design decision

**The LLM does not calculate the numerical risk score.** Risk scoring is deterministic, reproducible and auditable. GenAI is used for evidence-grounded explanation and mitigation planning.

## Architecture

```text
Streamlit
   |
FastAPI
   |
LangGraph
   |
   +--> Intent
   +--> Risk Scoring --------   +--> Supplier-scoped RAG --+--> Recommendations --> Validation --> LLM
```

The scoring and RAG branches are independent after intent and are structured so the graph runtime can execute them concurrently.

## Risk weights

Financial 30% | Operational 25% | Quality 20% | Compliance 15% | Geographic 10%

0–29 LOW | 30–59 MEDIUM | 60–79 HIGH | 80–100 CRITICAL

## Project

Use **SUP-0100 — Apex Components 100**.

The first screen shows a compact executive summary. Click **`⋯ More — complete answer`** to see the complete assessment.

Ask:
- Why is this supplier high risk?
- What should procurement do first?
- What evidence supports the recommendation?

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts_generate_data.py
```

Optional `.env`:

```text
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

Without an API key, an evidence-grounded deterministic fallback keeps the project functional.

## Run

Terminal 1:
```powershell
uvicorn app.api.main:app --reload --port 8000
```

Terminal 2:
```powershell
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`. Swagger is at `http://127.0.0.1:8000/docs`.

## Tests

```powershell
pytest -q
```

If LangGraph is not installed in the active virtual environment, run `pip install -r requirements.txt` first.

## Token optimization

- Risk calculation outside the LLM
- Supplier metadata filtering before synthesis
- Chunked evidence
- Top-K retrieval
- Compact prompts
- Low temperature
- Capped output
- Actual API token usage captured when available

## Latency optimization

- Local deterministic scoring
- In-memory FAISS
- Lightweight embedding model
- Supplier-scoped retrieval
- Cached supplier list
- Parallelizable LangGraph branches
- Small context/output budget

## Production roadmap

ERP/procurement integrations, event streaming, PostgreSQL/Redis, external intelligence, calibrated thresholds, RBAC, observability, human approval, model evaluation and alerting.

## Limitation

All data is synthetic and scoring weights are illustrative. Production use requires validated data, calibration, governance and human review.

### Synthetic dataset size
This capstone project uses **100 synthetic suppliers**. The dataset is intentionally
large enough to demonstrate varied risk profiles while keeping the project fast and
easy to inspect. The architecture is independent of dataset size and can scale
to much larger supplier populations in production.
