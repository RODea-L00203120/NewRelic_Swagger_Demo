# Tiny To-Do — New Relic Observability Lab

A minimal Flask + SQLite to-do app, instrumented step-by-step with New Relic
to demonstrate four observability tools:

1. **APM** — application performance monitoring (transactions, DB calls, errors)
2. **Logs in Context** — application log forwarding correlated with traces
3. **Browser monitoring** — real user metrics from the frontend
4. **Alerts & Dashboards** — NRQL queries, custom dashboards, alert conditions

Each tool is added on its own feature branch so the progression is visible in
`git log` and the branch graph.

This project accompanies the New Relic University courses below:

![New Relic University course completions](docs/screenshots/nr-university-courses.png)

## The app

A single-page Flask + SQLite to-do list — add, toggle done, delete:

![Tiny To-Do app running locally](docs/screenshots/app-running.png)

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

### Tool 1 — APM

The Python agent auto-instruments Flask request handling and the `sqlite3`
driver. Each route is recorded as a separate transaction; queries within a
transaction are captured as nested database segments.

- **Summary** — response time, throughput, error rate, Apdex
- **Transactions** — per-route metrics (`/`, `/add`, `/toggle/<int>`, `/delete/<int>`)
- **Databases** — auto-instrumented SQLite query timings
- **Distributed tracing** — request waterfall with nested spans
- **Errors inbox** — exceptions with stack traces and transaction context

The Transactions view groups requests by route. Each transaction's share of
total time consumed and average response time are visible without any manual
instrumentation:

![APM Transactions view for Tiny To-Do (Flask)](docs/screenshots/apm-transactions.png)

### Tool 2 — Logs in Context

Configured via `application_logging.forwarding.enabled = true` in
`newrelic.ini`. The agent attaches a handler to Python's root logger that
ships records (level, timestamp, message, plus the active `trace.id` and
`span.id`) to New Relic over the same channel as APM data. Because the
identifiers come from the active transaction, the UI can filter logs to a
specific request.

Exercising the app to generate log lines (`app.logger.info("added todo …")`,
`app.logger.warning("rejected empty todo title")`, etc.):

![Tiny To-Do with several added todos used to generate log activity](docs/screenshots/app-with-logging.png)

Opening a transaction trace and switching to the **Logs** sub-tab shows only
the log records emitted while that transaction was active — the correlation
is by `trace.id`, not by string matching:

![Transaction trace with Logs sub-tab showing the INFO log emitted during that request](docs/screenshots/logs-in-context.png)

The same data is queryable directly via NRQL. Example: every `added todo`
record in the last hour, with the message and correlation IDs:

```sql
SELECT * FROM Log WHERE message LIKE '%added todo%' SINCE 1 hour ago
```

![NRQL query in Data Explorer returning forwarded log records](docs/screenshots/nrql-logs-query.png)

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
