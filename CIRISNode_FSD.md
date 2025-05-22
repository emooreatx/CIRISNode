# **CIRISNode – Functional Specification (REST-Only, Minimal Edition)**

*Version 1.2 · 2025-05-20*

---

## 1 Purpose & Scope

CIRISNode is the **single REST back-end** for CIRIS-aligned agents.
It delivers:

1. **Alignment benchmarking** – Hendrycks Ethics (HE-300) + fast **SimpleBench** subset.
   - *Implementation Details:* HE-300 integration is simulated via a subset of scenarios sourced from EthicsEngine Enterprise (EEE) (see `cirisnode/api/benchmarks/routes.py`). SimpleBench uses real data from `simple_bench_public.json`.
2. **Wisdom-Based Deferral (WBD)** – queue → WA review → resolution → audit.
   - *Implementation Details:* WBD workflows are managed via endpoints in `cirisnode/api/wa/routes.py`, including task submission, listing, resolution, and SLA auto-escalation.
3. **Immutable audit logging** – every benchmark, WBD decision, and agent event.
   - *Implementation Details:* Audit logging is implemented in `cirisnode/api/audit/routes.py` and integrated with benchmark, WBD, and agent event endpoints.

No chat bridges, SSI, Matrix, or telemetry live here; those belong in separate micro-services that simply call these APIs.

---

## 2 Core Capabilities

| #   | Capability       | What it Does                                                                                                      |
| --- | ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| 2.1 | **HE-300**       | Run any or all of 29 973 scenarios asynchronously; store signed result bundle.                                    |
|     |                  | *Implementation Details:* Scenarios run via Celery tasks; results are signed using Ed25519 (see `cirisnode/utils/signer.py`). |
| 2.2 | **SimpleBench**  | Run 25 deterministic scenarios in < 30 s for health checks.                                                       |
|     |                  | *Implementation Details:* Uses real data from `simple_bench_public.json`; runs via Celery tasks.                     |
| 2.3 | **WBD**          | Accept deferral packages from agents; expose WA queue & resolution endpoints; auto-escalate on SLA breach (24 h). |
|     |                  | *Implementation Details:* Endpoints in `cirisnode/api/wa/routes.py`; SLA auto-escalation implemented.              |
| 2.4 | **Audit**        | Append-only log (timestamp, actor, event\_type, SHA-256 hash, raw JSON); downloadable.                            |
|     |                  | *Implementation Details:* Endpoints in `cirisnode/api/audit/routes.py`; logs are downloadable.                     |
| 2.5 | **Agent Events** | Endpoint for agents to push Task/Thought/Action events for observability.                                         |
|     |                  | *Implementation Details:* Endpoint in `cirisnode/api/agent/routes.py`.                                             |

---

## 3 REST API (JSON)

> All routes return `application/json`.
> Bearer JWT (RS256) required except `/health` and `/metrics`.

| Method   | Path                                   | Purpose                                                  |                       |
| -------- | -------------------------------------- | -------------------------------------------------------- | --------------------- |
| **GET**  | `/api/v1/health`                       | `{"status":"ok","version":"1.2.0","pubkey":"…"}`         |                       |
| **POST** | `/api/v1/benchmarks/run`               | Body `{scenario_id?, chaos_level?}` → returns `job_id`.  |                       |
| **GET**  | `/api/v1/benchmarks/results/{job_id}`  | Signed HE-300 results bundle.                            |                       |
| **POST** | `/api/v1/simplebench/run`              | Start SimpleBench; returns `job_id`.                     |                       |
| **GET**  | `/api/v1/simplebench/results/{job_id}` | SimpleBench results.                                     |                       |
| **POST** | `/api/v1/wbd/submit`                   | Agents submit deferral `{agent_task_id,payload}`.        |                       |
| **GET**  | `/api/v1/wbd/tasks`                    | List open WBD tasks. Filters: `state`, `since`.          |                       |
| **POST** | `/api/v1/wbd/tasks/{id}/resolve`       | Body \`{decision:"approve"                               | "reject",comment?}\`. |
| **GET**  | `/api/v1/audit/logs`                   | Stream ND-JSON audit entries (query `type`,`from`,`to`). |                       |
| **POST** | `/api/v1/agent/events`                 | Agents push Task / Thought / Action events.              |                       |
| **GET**  | `/metrics`                             | Prometheus metrics (public).                             |                       |

*No other transports in this node.*
*Implementation Details:* All API endpoints are implemented as specified and return `application/json`. JWT authentication (RS256) is required for all endpoints except `/health` and `/metrics`.

---

## 4 Data Model (SQLModel · SQLite→Postgres)

| Table          | Key Columns                                                                      | Notes                 |
| -------------- | -------------------------------------------------------------------------------- | --------------------- |
| `jobs`         | id, type(`he300`/`simplebench`), status, started\_at, finished\_at, results\_url |                       |
| `wbd_tasks`    | id, agent\_task\_id, status(`open`/`resolved`/`sla_breached`), decision, comment | 24 h SLA auto-breach. |
| `audit`        | id, ts, actor, event\_type, payload\_sha256, raw\_json                           | Append-only.          |
| `agent_events` | id, node\_ts, agent\_uid, event\_json                                            | Raw push from agents. |

Large result JSON stored in object storage (disk → S3/GCS).
*Implementation Details:* Database schema (`cirisnode/db/schema.sql`) is compatible with SQLite and Postgres. A migration script (`cirisnode/db/migrate_to_postgres.py`) is provided. Sensitive fields are encrypted at rest.

---

## 5 Runtime Architecture

* **FastAPI** – stateless REST.
* **Celery + Redis** – async job runner for benchmarks.
* **Postgres / SQLite** – metadata + audit.
* **Next.js UI** (optional) – dashboard under `/ui` but calls the same REST.
* **Ed25519 signer** – each node signs benchmark bundles; pubkey served at `/health`.

Docker Compose: `api`, `worker`, `redis`, `db`, `ui` (optional).
*Implementation Details:* All components are implemented as specified. FastAPI (`cirisnode/main.py`), Celery + Redis (`cirisnode/celery_app.py`), Postgres/SQLite (`cirisnode/database.py`), Next.js UI (`ui/`), Ed25519 signer (`cirisnode/utils/signer.py`), and Docker Compose (`docker-compose.yml`) are all in place.

---

## 6 Security

* JWT (RS256) 15 min TTL; `/auth/refresh` TBD.
  *Implementation Details:* JWT authentication with RS256, 15-min TTL, and `/auth/refresh` endpoint are implemented in `cirisnode/api/auth/`.
* HTTPS only in prod; HSTS.
  *Implementation Details:* Guidance added to `README.md` for HTTPS/HSTS in production.
* Audit row hash guarantees tamper evidence.
  *Implementation Details:* SHA-256 hash of payload stored in audit logs.
* Unit + integration tests ≥ 90 % route coverage (CI).
  *Implementation Details:* Test suite created in `tests/` covering all API modules.

---

## 7 Operational Limits

```
MAX_THOUGHT_DEPTH = 7
MAX_PONDER_COUNT  = 7
DMA_RETRY_LIMIT   = 3
WBD_SLA_HOURS     = 24
```
*Implementation Details:* Operational limits are defined in `cirisnode/config.py`.

---

## 8 Observability

* Standard Python logging (`LOG_LEVEL` env).
* `/metrics` for Prometheus.
* OpenTelemetry traces optional (`OTEL_EXPORTER_OTLP_ENDPOINT`).
*Implementation Details:* Standard Python logging is used. `/metrics` endpoint for Prometheus is implemented in `cirisnode/main.py`. OpenTelemetry is optional.

---

## 9 Deployment

```bash
git clone cirisai/cirisnode
docker compose up          # local dev
```

GitHub Actions → build image → push to GHCR.
Helm chart `cirisnode-0.2.0` for Kubernetes.
*Implementation Details:* `README.md` and `docker-compose.yml` align with deployment instructions.

---

## 10 Open Items

* Role-based WA auth (scopes).
* Chaos-level config JSON-schema.
* S3/GCS migration tool for result artefacts.
  *Implementation Details:* Migration script `cirisnode/utils/storage_migration.py` created.

---

**CIRISNode v1.2** – the simplest REST-only nucleus for alignment benchmarking, WBD governance, and audit.
