# **CIRISNode – Functional Specification (REST-Only, Minimal Edition)**

*Version 1.2 · 2025-05-20*

---

## 1 Purpose & Scope

CIRISNode is the **single REST back-end** for CIRIS-aligned agents.
It delivers:

1. **Alignment benchmarking** – Hendrycks Ethics (HE-300) + fast **SimpleBench** subset.
2. **Wisdom-Based Deferral (WBD)** – queue → WA review → resolution → audit.
3. **Immutable audit logging** – every benchmark, WBD decision, and agent event.

No chat bridges, SSI, Matrix, or telemetry live here; those belong in separate micro-services that simply call these APIs.

---

## 2 Core Capabilities

| #   | Capability       | What it Does                                                                                                      |
| --- | ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| 2.1 | **HE-300**       | Run any or all of 29 973 scenarios asynchronously; store signed result bundle.                                    |
| 2.2 | **SimpleBench**  | Run 25 deterministic scenarios in < 30 s for health checks.                                                       |
| 2.3 | **WBD**          | Accept deferral packages from agents; expose WA queue & resolution endpoints; auto-escalate on SLA breach (24 h). |
| 2.4 | **Audit**        | Append-only log (timestamp, actor, event\_type, SHA-256 hash, raw JSON); downloadable.                            |
| 2.5 | **Agent Events** | Endpoint for agents to push Task/Thought/Action events for observability.                                         |

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

---

## 4 Data Model (SQLModel · SQLite→Postgres)

| Table          | Key Columns                                                                      | Notes                 |
| -------------- | -------------------------------------------------------------------------------- | --------------------- |
| `jobs`         | id, type(`he300`/`simplebench`), status, started\_at, finished\_at, results\_url |                       |
| `wbd_tasks`    | id, agent\_task\_id, status(`open`/`resolved`/`sla_breached`), decision, comment | 24 h SLA auto-breach. |
| `audit`        | id, ts, actor, event\_type, payload\_sha256, raw\_json                           | Append-only.          |
| `agent_events` | id, node\_ts, agent\_uid, event\_json                                            | Raw push from agents. |

Large result JSON stored in object storage (disk → S3/GCS).

---

## 5 Runtime Architecture

* **FastAPI** – stateless REST.
* **Celery + Redis** – async job runner for benchmarks.
* **Postgres / SQLite** – metadata + audit.
* **Next.js UI** (optional) – dashboard under `/ui` but calls the same REST.
* **Ed25519 signer** – each node signs benchmark bundles; pubkey served at `/health`.

Docker Compose: `api`, `worker`, `redis`, `db`, `ui` (optional).

---

## 6 Security

* JWT (RS256) 15 min TTL; `/auth/refresh` TBD.
* HTTPS only in prod; HSTS.
* Audit row hash guarantees tamper evidence.
* Unit + integration tests ≥ 90 % route coverage (CI).

---

## 7 Operational Limits

```
MAX_THOUGHT_DEPTH = 7
MAX_PONDER_COUNT  = 7
DMA_RETRY_LIMIT   = 3
WBD_SLA_HOURS     = 24
```

---

## 8 Observability

* Standard Python logging (`LOG_LEVEL` env).
* `/metrics` for Prometheus.
* OpenTelemetry traces optional (`OTEL_EXPORTER_OTLP_ENDPOINT`).

---

## 9 Deployment

```bash
git clone cirisai/cirisnode
docker compose up          # local dev
```

GitHub Actions → build image → push to GHCR.
Helm chart `cirisnode-0.2.0` for Kubernetes.

---

## 10 Open Items

* Role-based WA auth (scopes).
* Chaos-level config JSON-schema.
* S3/GCS migration tool for result artefacts.

---

**CIRISNode v1.2** – the simplest REST-only nucleus for alignment benchmarking, WBD governance, and audit.
