# Grade Evidence Certainty Agent

A reviewer-driven GRADE certainty-of-evidence calculator for **intervention outcomes**, with additional legacy numeric-alert utilities retained for compatibility. The GRADE calculator documents assessor-entered domain judgments; it does not automatically appraise study quality, derive judgments from effect estimates, or recommend treatment.

## Browser application

Open `web/index.html` in a modern browser to calculate a GRADE rating locally and export the assessment as JSON. No server, Python interpreter, API key, external JavaScript, network request, analytics, or local storage is needed. The `web/` directory is also suitable for static hosting; an automated GitHub Pages deployment workflow is included. The live URL should be treated as available only after a successful Pages deployment.

The browser form supports the conventional approach for intervention outcomes:

- **Starting certainty:** high for randomized trials; low for non-randomized studies.
- **Downgrading:** risk of bias, inconsistency, indirectness, imprecision, and publication bias, each 0–2 levels.
- **Upgrading:** magnitude of effect (0–2), credible dose–response gradient (0–1), and opposing residual confounding (0–1), only for low-start non-randomized evidence without downgrades.
- **Output:** very low / low / moderate / high, with transparent judgment breakdown and local JSON export.

This calculator does not implement the alternative ROBINS-I-based high-start approach or decide whether judgments are clinically justified. See the [GRADE Book overview](https://book.gradepro.org/guideline/overview-of-the-grade-approach).

## Installation and command line

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[api,test]"
grade-evidence-certainty-engine grade --design randomized --risk-of-bias 1 --imprecision 1
grade-evidence-certainty-engine grade --design observational --large-effect 1 --dose-response 1
python -m pytest -q
node --test web/app.test.js
```

The `grade` command prints a machine-readable JSON assessment and rejects invalid or ineligible upgrades.

### REST endpoint

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

`POST /api/grade` accepts JSON with `study_design` (`randomized` or `observational`) and optional integer GRADE domains named `risk_of_bias`, `inconsistency`, `indirectness`, `imprecision`, `publication_bias`, `large_effect`, `dose_response`, `plausible_confounding`. For example:

```bash
curl -s -X POST http://127.0.0.1:8000/api/grade \
  -H 'Content-Type: application/json' \
  -d '{"study_design":"randomized","risk_of_bias":1,"imprecision":1}'
```

The existing `/api/audit`, `/api/chat`, `/api/audit/logs`, `/health`, and `/metrics` endpoints remain available. Their legacy threshold-alert behavior is **not GRADE appraisal**.

## Legacy operations

The repository also includes the original `agents/` rule-based supervisor, `grade_master.py`, `grade_evidence_certainty_agent/` metric audit, `enrichment.py`, and related CLIs. They are retained to avoid breaking existing integrations:

```bash
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i operations.csv -o results.csv
python cli.py verify-audit
python grade_master.py audit
grade-evidence-certainty-engine batch -i sample.csv -o results.csv
```

The `sample.csv` schema applies to the packaged legacy batch command, not the root operations CLI. The original thresholds and references are demonstration rules, not validated clinical alerts or official GRADE domain rules.

## Privacy and deployment

The **browser tool** runs locally and processes the fields without transmitting or storing them. The **Python API** holds dossiers and an HMAC-linked audit chain in process memory; that chain is not persistent storage and does not replace a compliance-grade audit system. The pattern-based identifier guard is limited and **does not guarantee de-identification or HIPAA compliance**. Avoid real patient information. The HTTP API has no authentication; **do not expose it to the public internet** without adding access control, transport security, and operational safeguards.

To run locally in Docker:

```bash
cp .env.example .env
# Replace AUDIT_SECRET_KEY with a strong random value before running.
docker compose up --build
```

Compose binds to `127.0.0.1:8000` by default. `.dockerignore` excludes local `.env` files from container builds.

## Development and validation

Python dependencies are declared in `pyproject.toml`; CI tests Python 3.10–3.13, builds the distribution, runs pytest, validates the browser JavaScript with Node, and tests the HMAC chain. GitHub Pages deployment uses the `web/` directory when Pages is enabled for GitHub Actions. The browser interface uses standard HTML, CSS and JavaScript and targets current desktop/mobile browsers; it does not require Pyodide because the browser calculation is already fully client-side.

**License:** MIT (see [LICENSE](LICENSE)).
