# Tiny To-Do — New Relic Observability Lab

A minimal Flask + SQLite to-do app, instrumented step-by-step with New Relic
to demonstrate four observability tools:

1. **APM** — application performance monitoring (transactions, DB calls, errors)
2. **Logs in Context** — application log forwarding correlated with traces
3. **Browser monitoring** — real user metrics from the frontend
4. **Alerts & Dashboards** — NRQL queries, custom dashboards, alert conditions

Each tool is added in its own commit so the progression is visible in `git log`.

## Prerequisites

- A free New Relic account: https://newrelic.com/signup
- An **INGEST - LICENSE** key (created via *user menu → API keys → Create a key*)
- Either:
  - **VS Code + Docker Desktop** (to use the included dev container — recommended), or
  - Python 3.12+ locally

## Setup

### 1. Clone and open

```bash
git clone git@github.com:RODea-L00203120/NewRelic_Swagger_Demo.git
cd NewRelic_Swagger_Demo
```

If using VS Code: Command Palette → **Dev Containers: Reopen in Container**.
Otherwise create a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements-dev.txt
```

`requirements-dev.txt` includes the runtime deps plus `black` and `flake8` for
linting/formatting.

### 3. Configure your New Relic credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
NEW_RELIC_LICENSE_KEY=<paste-unmasked-INGEST-LICENSE-key-here>
NEW_RELIC_REGION=eu                       # or "us" depending on your account
NEW_RELIC_APP_NAME="Tiny To-Do (Flask)"
```

> The license key MUST be the unmasked value shown in the modal when the key
> is created — not the masked preview from the API keys table, and not the
> key ID.

`.env` is gitignored. `newrelic.ini` is committed but contains no secrets;
the agent reads `NEW_RELIC_LICENSE_KEY` from the environment.

### 4. Run with the agent wrapper

```bash
set -a; source .env; set +a
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python app.py
```

Open the forwarded port from the VS Code **Ports** panel (the row labelled
"Flask app (5000)"), or http://localhost:5000 if running locally.

### 5. Verify data is reaching New Relic

```bash
newrelic-admin validate-config newrelic.ini
```

Should print `Registration successful`.

Then in https://one.newrelic.com → **APM & Services**, the entity
**Tiny To-Do (Flask)** should appear within ~60 seconds of the first request.

## What to look at in the New Relic UI

For tool 1 (APM):

- **Summary** — response time, throughput, error rate, Apdex
- **Transactions** — per-route metrics (`/`, `/add`, `/toggle/<int>`, `/delete/<int>`)
- **Databases** — auto-instrumented SQLite query timings
- **Distributed tracing** — request waterfall with nested spans
- **Errors inbox** — exceptions with stack traces and transaction context

## Code style

```bash
black .
flake8
```

Configured in `pyproject.toml` and `.flake8` respectively. Black handles
formatting; flake8 catches issues Black doesn't (unused imports, undefined
names, etc).

## Troubleshooting

- **`externally-managed-environment` on `pip install`** — you're outside the
  dev container on a host with PEP 668. Use the dev container or create a
  venv.
- **`Forbidden` when opening the forwarded port** — Flask is bound to
  `127.0.0.1`. The app is configured for `0.0.0.0`; if you've changed it,
  revert.
- **`incorrect license key` errors in agent log** — check `NEW_RELIC_REGION`
  matches your account, and ensure `newrelic.ini` does not have any
  `license_key = ...` line (the file overrides env vars, so even an empty
  line wins over `NEW_RELIC_LICENSE_KEY`).
- **No data in NR after 2 minutes** — restart the server after editing
  `.env`; env vars are read at process start, not re-read mid-run.
