# Grade Evidence Certainty Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI
> **Reference Guidelines & Standards:** `American College of Radiology (ACR) RADS & Fleischner Society`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Grade Evidence Certainty Agent** is an advanced analytical and computational platform implementing a multi-agent consensus engine for clinical task evaluation. It dispatches tasks across specialized worker agents that evaluate metrics against domain-specific thresholds, producing a consensus dossier with HMAC-SHA256 audit trail.

---

## Key Capabilities & Algorithmic Modules

### Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`RiskOfBiasSynthesizerAgent`**: Specialized Sub-Agent 1 for grade-evidence-certainty-agent
- **`HeterogeneityImprecisionAgent`**: Specialized Sub-Agent 2 for grade-evidence-certainty-agent
- **`CertaintyGradeAggregatorAgent`**: Specialized Sub-Agent 3 for grade-evidence-certainty-agent

### Project Structure

```
grade-evidence-certainty-agent/
├── agents/                    # Core multi-agent system
│   ├── base.py               # PHI guard, HMAC-SHA256 audit trail
│   ├── models.py             # Pydantic v2 data models
│   ├── workers.py            # Specialized domain workers
│   ├── supervisor.py         # Master coordinator
│   ├── api.py                # FastAPI REST endpoints
│   ├── llm_factory.py        # LLM provider abstraction
│   └── ...
├── cli.py                    # Command-line entry point
├── grade_master.py           # Standalone GRADE-Master implementation
├── enrichment.py             # Additional enrichment features
├── tests/                    # Test suite
├── web/                      # Operations console (HTML)
├── Dockerfile                # Container definition
└── docker-compose.yml        # Docker orchestration
```

---

## Quickstart

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic pytest
```

### 2. Configure Environment

Copy the example environment file and set your secure audit key:

```bash
cp .env.example .env
# Edit .env and set a secure AUDIT_SECRET_KEY
# Generate one: python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run the CLI

```bash
# Single task evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT

# Batch processing
python cli.py batch -i sample.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Interactive chat
python cli.py chat "What is the system status?"

# Launch REST server
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or specimen key | Required |
| `primary_metric` | Primary domain measurement | Required |
| `secondary_metric` | Secondary kinetic score | Optional (default 0.0) |
| `status_descriptor` | Status code or phenotype | Optional (default "NOMINAL") |
| `is_critical_flag` | Emergency escalation flag | Optional (default false) |

---

## Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Requires `AUDIT_SECRET_KEY` environment variable (minimum 16 characters).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).
* **Input Validation:** All metric values are validated as finite numbers (NaN/infinity rejected).

---

## Testing & Verification

Set the audit key, then run the automated test suite:

```bash
export AUDIT_SECRET_KEY="test-key-that-is-long-enough-12345"
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## Container Deployment

```bash
# Configure environment first
cp .env.example .env
# Edit .env with your secure key

# Build and run
docker compose up --build
# Or with Docker directly:
docker build -t grade-evidence-certainty-agent .
docker run -p 8000:8000 --env-file .env grade-evidence-certainty-agent
```

---

## Environment Variables

| Variable | Required | Description |
|:---------|:---------|:------------|
| `AUDIT_SECRET_KEY` | Yes | HMAC-SHA256 signing key (min 16 chars) |
| `MODEL_PROVIDER` | No | LLM provider: `mock` (default), `ollama`, `claude`, `openai` |
