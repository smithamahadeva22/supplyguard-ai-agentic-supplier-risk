# SupplyGuard AI — Short Solution Report

## Objective
Predict and explain supplier risk in a supply-chain environment using an agentic workflow.

## Solution
Synthetic supplier KPIs and events feed a deterministic risk engine. Supplier-specific evidence is retrieved using RAG. LangGraph orchestrates intent, scoring, retrieval, recommendations, validation and synthesis. The LLM produces a concise evidence-grounded assessment.

## Architecture
```text
UI -> FastAPI -> LangGraph
                 ├─ Intent
                 ├─ Risk Engine
                 ├─ RAG
                 ├─ Recommendations
                 ├─ Validation
                 └─ LLM Synthesis
```

## Why deterministic scoring?
A procurement risk score should be reproducible, testable and auditable. The LLM should not silently change a business-critical numerical decision.

## RAG
Reports are split into sections and indexed with Sentence Transformers + FAISS. Retrieval is constrained by supplier ID, preventing unrelated supplier evidence from entering the synthesis context.

## Token optimization
Only relevant top-K evidence is sent to the model; calculations happen outside the LLM; prompts are compact; output is capped; usage is measured.

## Latency optimization
Local scoring, in-memory FAISS, supplier filtering, UI caching and independent graph branches reduce unnecessary work.

## Explainability
The UI exposes overall score, dimension drivers, evidence, recommendations, validation and diagnostics.

## Practicality
The project separates risk logic, retrieval, orchestration, LLM provider, API and UI, making production replacement straightforward.

## Limitations
Synthetic data, illustrative weights, no external intelligence, and no production security/integration layer.
