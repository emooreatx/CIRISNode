# CIRISNode

> Alignment & governance back-plane for the CIRIS ecosystem  
> Status: **DEVELOPMENT — functional with stubbed integrations**

---

## 1  Overview

CIRISNode (née “EthicsEngine Enterprise”) is the remote utility that CIRISAgent clients will call for:

- **Alignment benchmarking** (Annex J HE-300 suite)  
- **Secure communications** via a Matrix homeserver integration  
- **Governance workflows** (WA ticketing, audit anchoring)  
- **SSI/DID support** through a Hyperledger Aries side-car

---

## 2  Core Responsibilities

1. **Alignment API**  
   Runs HE-300 scenarios, enforces pass/fail gates, returns signed benchmark reports.

2. **WA API**  
   Receives Wisdom-Based Deferral packages, relays to Wise Authorities, streams replies.

3. **SSI/DID API**  
   Issues and verifies W3C DIDs and verifiable credentials for audit roots and reports.

4. **Audit Anchoring**  
   Publishes daily SHA-256 roots of logs and benchmark results into a Matrix “transparency” room and mints them as `CIRIS-AuditRoot` credentials.

---

## 3  API Endpoints

- **GET** /api/v1/health  
- **POST** /api/v1/did/issue → `{ did, verkey, token }`  
- **POST** /api/v1/did/verify → verification result  
- **POST** /api/v1/matrix/token → Matrix access token  
- **POST** /api/v1/benchmarks/run → start HE-300  
- **GET** /api/v1/benchmarks/status/{run_id}  
- **GET** /api/v1/benchmarks/results/{run_id} → signed report + VC  
- **POST** /api/v1/wa/ticket → submit deferral package  
- **GET** /api/v1/wa/status/{ticket_id}

*All responses are JSON-Web-Signed; clients verify via the Aries agent.*

---

## 4  SSI / DID Integration

- Aries side-car issues Verifiable Credentials for:
  - Benchmark reports (`CIRIS-BenchReport`)  
  - Daily audit roots (`CIRIS-AuditRoot`)  

- Agents authenticate using short-lived, DID-scoped tokens.  
- Matrix access is granted via Aries-issued tokens bound to each DID.

---

## 5  Naming & Migration Plan

- References to “EthicsEngine Enterprise” will be renamed to **CIRISNode** once Matrix & SSI flows stabilize.  
- Documentation will use “CIRISNode (née EthicsEngine Enterprise)” until final branding is confirmed.  
- **TBD**: exact Matrix room IDs, Aries agent configuration parameters, governance charter hooks.

---

## 6  Next Steps

- Draft OpenAPI specification for `/api/v1/*` endpoints.  
- Design architecture and data-flow diagrams.  
- Prototype Aries integration and Matrix provisioning scripts.  
- Migrate existing EEE documentation into this new spec as code is developed.

---

## 7  License

This README is licensed under Apache 2.0 © 2025 CIRIS AI Project

---

## Bradley Matera's Operational Extension Notes

### CIRISNode Development Status as of May 5, 2025

This section outlines everything completed during Phase 2 and the beginning of Phase 3 of CIRISNode’s development. I took the project from a conceptual state with no working code or containers and built a fully functional FastAPI backend. The system now includes working support for JWT-based authentication, Matrix chat integration, execution of HE-300 benchmark scenarios, DID issuance and verification endpoints, and Wisdom Authority ticketing workflows. All major API routes have been implemented, tested, and verified. The system is now containerized with Docker, runs end-to-end locally or in CI, and has a fully passing test suite covering its core features. Additionally, a standalone frontend interface for the Ethics Engine Enterprise (EEE) system has been developed as part of Phase 1 of the frontend rollout.

---

### Completed Work Summary

#### API Layer

- Fully implemented all endpoints listed in section `3 API Endpoints`
- Each route structured into modular FastAPI routers across:
  - `cirisnode/api/benchmarks/routes.py`
  - `cirisnode/api/wa/routes.py`
  - `cirisnode/api/did/routes.py`

---

#### Authentication

- JWT-based route protection added using FastAPI middleware
- Token issued via `/api/v1/did/issue`
- All sensitive endpoints require `Authorization: Bearer <token>`

---

#### Matrix Integration

- Matrix access tokens can be issued via `/api/v1/matrix/token`
- Background task (`audit_anchoring`) implemented to send SHA-256 root summaries to a Matrix transparency room
- Matrix integration is fully async-compatible

---

#### Ethical Pipeline (HE-300/EEE)

- Core HE-300 benchmark logic included
- Benchmark runs triggered via `/api/v1/benchmarks/run`
- Results are saved and accessible via `/status/{id}` and `/results/{id}`
- Placeholder inference logic is located in `utils/inference.py`

---

#### DID / SSI Support (Stub)

- Aries agent integration is currently **stubbed**
- DID issuance returns placeholder keys and tokens
- Verification endpoint accepts sample payloads and returns deterministic responses
- To be replaced with actual Aries RFC-compliant handlers in Phase 3

---

#### Audit Anchoring

- A daily task (via APScheduler) publishes digests of benchmark activity
- SHA-256 hash + timestamp stored
- Emitted to Matrix channel and intended for use as a CIRIS-AuditRoot VC

---

#### Docker + CI/CD Support

- Dockerfile created to build and run app with `uvicorn --workers`
- Docker-based test container enabled (copies `tests/` folder and runs pytest)
- GitHub Actions workflow (`.github/workflows/test.yml`) added to auto-run tests on push and pull requests
- `.env` file integrated via `python-dotenv` and used for secrets/config

---

#### Frontend Interface for EEE (Phase 1 Complete)

A full offline-ready Streamlit interface for Wise Authorities (WAs) has been developed and added to the repo at frontend_eee/main.py. The frontend simulates ethical processing and decision-making workflows using mock data (stored in frontend_eee/mock_data.py) and includes the following panels:
	•	Deferral Inbox: Review and take action on ponder, reject, and defer requests.
	•	Thought Queue Viewer: Displays queued DMA actions with mock metadata.
	•	DMA Actions Panel: Trigger mock actions such as listen, speak, ponder, and useTool.
	•	Graph Interaction Panel: View and manipulate mock versions of ID_GRAPH, ENV_GRAPH, and JOB_GRAPH. Includes controls for learn, remember, and forget.
	•	Guardrail & Faculty Panel: Simulate entropy, coherence, and round number values per DMA cycle.
	•	Ethical Benchmark Simulation: Button to log mock runs for future benchmarking and analysis.

The interface runs 100% offline and does not require any API keys or real backend connectivity.

🐳 Docker Integration (Phase 2 Ready)

This frontend is now containerized and integrated into the docker-compose.yml file alongside the backend FastAPI app. Running both together enables real-time local testing and future backend binding. To launch:

docker-compose up --build

Then visit:
	•	Frontend UI: http://localhost:8501
	•	Backend API: http://localhost:8002/docs

---

### 🛠 Setup Instructions

This section provides detailed, step-by-step instructions to set up and run CIRISNode on your local machine or in a Docker container. Follow these steps carefully to ensure a successful setup.

#### Prerequisites

- **Python 3.10+**: Ensure Python 3.10 or higher is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Required to clone the repository. Install from [git-scm.com](https://git-scm.com/downloads).
- **Docker**: Optional, for containerized setup. Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).
- **Virtual Environment**: Recommended for isolating project dependencies.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/BradleyMatera/CIRISNode
cd CIRISNode
```

#### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment to manage project dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

#### Step 3: Install Dependencies

Install the required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory with the necessary environment variables. Use the following template as a starting point:

```env
# General Configuration
ENVIRONMENT=dev
JWT_SECRET=supersecretkey

# Matrix Configuration
MATRIX_LOGGING_ENABLED=false
MATRIX_HOMESERVER_URL=https://matrix.example.org
MATRIX_ACCESS_TOKEN=dummytoken
MATRIX_ROOM_ID=!room:matrix.org

# Authorization Configuration
ALLOWED_BLESSED_DIDS=did:example:12345
ALLOWED_BENCHMARK_IPS=127.0.0.1
ALLOWED_BENCHMARK_TOKENS=sk_test_abc123
```

- **ENVIRONMENT**: Set to `dev` for development, `test` for testing, or `prod` for production. This affects authentication bypass and API documentation visibility.
- **JWT_SECRET**: A secret key for signing JWT tokens. Replace with a secure value in production.
- **MATRIX_LOGGING_ENABLED**: Set to `true` to enable Matrix logging, `false` to disable.
- **MATRIX_HOMESERVER_URL**, **MATRIX_ACCESS_TOKEN**, **MATRIX_ROOM_ID**: Configure these for Matrix integration if enabled. Use placeholder values if not using Matrix.
- **ALLOWED_BLESSED_DIDS**, **ALLOWED_BENCHMARK_IPS**, **ALLOWED_BENCHMARK_TOKENS**: Define allowed DIDs, IPs, and tokens for benchmark access. Adjust for your test or production environment.

#### Step 5: Run the Server Locally

Start the FastAPI server using `uvicorn` with auto-reload enabled for development.

```bash
uvicorn cirisnode.main:app --reload --port 8001
```

- The server will run on `http://localhost:8001`.
- Access the health check endpoint at `http://localhost:8001/api/v1/health` to confirm the server is running (should return `{"status": "ok"}`).
- Explore the API documentation at `http://localhost:8001/docs` (available in `dev` or `test` environments).

#### Step 6: Run the Test Suite Locally

Ensure your environment is set to `test` by setting `ENVIRONMENT=test` in your `.env` file or by using environment variables in the command. Install test dependencies if not already installed, then run the tests.

```bash
pip install pytest pytest-asyncio pytest-env httpx
pytest tests/ -v
```

- Tests cover health checks, JWT authentication, benchmark workflows, DID issuance/verification, and more.
- Ensure `ENVIRONMENT=test` to enable test-specific bypass logic for protected routes.

#### Step 7: Run Using Docker (Optional)

For a containerized setup, use Docker to build and run CIRISNode.

1. **Build the Docker Image**

```bash
docker build -t cirisnode:latest .
```

2. **Run the Container**

```bash
docker run -d -p 8001:8001 --env-file .env --name cirisnode cirisnode:latest
```

- Maps port 8001 on your host to port 8001 in the container.
- Uses the `.env` file for environment variables.
- Access the health check at `http://localhost:8001/api/v1/health`.

3. **View Container Logs**

```bash
docker logs cirisnode
```

4. **Stop the Container**

```bash
docker stop cirisnode
docker rm cirisnode
```

#### Step 8: Run Tests in Docker (Optional)

To run the test suite inside a Docker container, modify the Dockerfile or create a separate test image.

1. **Create a Test Dockerfile or Modify Existing**

Add the following to your `Dockerfile` or create a separate `Dockerfile.test`:

```dockerfile
# Install test dependencies
RUN pip install pytest pytest-asyncio pytest-env httpx

# Copy test files
COPY ./tests /app/tests

# Set environment for testing
ENV ENVIRONMENT=test

# Command to run tests
CMD ["pytest", "-v", "tests/"]
```

2. **Build and Run Test Container**

```bash
docker build -t cirisnode-test:latest -f Dockerfile.test .
docker run --rm --env-file .env cirisnode-test:latest
```

- `--rm` automatically removes the container after execution.
- Outputs test results to the console.

#### Step 9: Export OpenAPI Specification

If you want to save the OpenAPI specification for documentation or client generation:

```bash
curl http://localhost:8001/openapi.json > docs/api-spec/openapi.json
```

- Ensure the server is running on port 8001.
- The OpenAPI JSON will be saved to `docs/api-spec/openapi.json`.

---

### Errors and Troubleshooting

- **Connection Reset by Peer or "Not Found" Error when accessing http://localhost:8000/api/v1/health**: This error occurs if you are trying to access the application on the wrong port. CIRISNode runs on port 8001 by default, not 8000. Ensure you access `http://localhost:8001/api/v1/health`. If using Docker, verify the port mapping with `-p 8001:8001` in your `docker run` command. If the issue persists, check if the server or container is running with `ps aux | grep uvicorn` or `docker ps`, and restart if necessary.

- **Docker Build Fails with "No such file or directory: 'requirements.txt'"**: This happens if `requirements.txt` is missing or not in the project root. Generate it by running `pip freeze > requirements.txt` in your virtual environment before building the image. Ensure the file is committed to the repository if cloning from GitHub.

- **Unable to Access API Endpoints**: If endpoints return errors or are inaccessible:
  - Confirm the server is running (`ps aux | grep uvicorn` or `docker ps` for containers).
  - Check logs for startup errors (`docker logs <container_id>` if using Docker).
  - Verify the `.env` file exists and contains required variables like `JWT_SECRET`. Ensure `--env-file .env` is used in `docker run` commands.
  - Test the health endpoint at `http://localhost:8001/api/v1/health`. A response of `{"status": "ok"}` indicates the server is operational.
  - Access the interactive Swagger UI at `http://localhost:8001/docs` to explore and test endpoints directly from a browser (available in `dev` or `test` environments). Note that some endpoints require authentication headers.

- **Test Failures Due to Environment Configuration**: If tests fail with authentication errors, ensure `ENVIRONMENT=test` is set in your `.env` file or as an environment variable when running `pytest`. This enables bypass logic for protected routes during testing.

- **Matrix Logging Errors**: If Matrix logging is enabled (`MATRIX_LOGGING_ENABLED=true`) but credentials or URLs are incorrect, you’ll see errors in logs. Set `MATRIX_LOGGING_ENABLED=false` in `.env` to disable Matrix integration, or provide valid Matrix configuration values.

- **General Dependency Issues**: If `pip install` fails or dependencies conflict, ensure you're using Python 3.10+ and a clean virtual environment. Remove and recreate the virtual environment if needed (`rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`).

For additional help, check the GitHub repository issues or contact the project maintainers.

---

### 🧪 Test Suite Coverage

All test files are located in `tests/` and cover:
- `/health` endpoint
- JWT issuance and protection
- Matrix message sending
- Benchmark run and result lifecycle (HE-300)
- DID issuance and verification
- WA ticket submission and tracking
- AI ethical inference (EEE logic)
- Async support (with `pytest-asyncio`)
- Config loading from `.env`

---

### 🔒 Security

- Routes are protected by JWT.
- JWTs are issued per DID.
- Matrix access is scoped by token.
- `.env` secrets must be protected in deployment. Never commit `.env` to version control; use `.env.example` for templates.

---

### 🔍 Still To Do (Phase 3)

Not yet implemented as of this commit:

- Aries Agent full implementation (RFC 0036, 0037, etc.)
- Live Matrix token exchange using login API
- Proper Verifiable Credential issuance (via Aries)
- Secure EEE pipeline replacement for current stubs
- Swagger UI redirect at root (/)
- Helm chart or ECS definition for AWS-based deploy
- Persistent DB for audit and pipeline storage
- External authentication key store for DID + Matrix

---

### 📂 EEE / EthicsEngine Note

The original EthicsEngine Enterprise Edition (EEE) benchmark suite is included as a legacy reference. Current behavior mimics that system using deterministic stub logic located in:

`cirisnode/utils/inference.py`

Future iterations should integrate a pluggable AI backend or use Ollama-compatible local inference engines with ethical prompt encoding.

---

### 🧵 Final Word

CIRISNode is now fully operational in dev/test environments with full API, Matrix, and testing infrastructure, supporting future integration into the CIRISAgent client ecosystem and Hyperledger Aries stack. The addition of the EEE frontend interface marks the beginning of Phase 3, providing a mockable, modular UI for Wise Authorities to interact with the system offline, paving the way for full integration in upcoming phases.

– Bradley Matera, May 2025
