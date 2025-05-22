# CIRISNode

> Alignment & governance back-plane for the CIRIS ecosystem  
> Status: **DEVELOPMENT — functional with stubbed integrations**

---

## 1  Overview

CIRISNode is the remote utility that CIRISAgent clients will call for:

- **Alignment benchmarking** (Annex J HE-300 suite)  
- **Governance workflows** (WA ticketing, audit anchoring)  

---

## 2  Core Responsibilities

1. **Alignment API**  
   Runs HE-300 scenarios, enforces pass/fail gates, returns signed benchmark reports.

2. **WA API**  
   Receives Wisdom-Based Deferral packages, relays to Wise Authorities, streams replies.

3. **Audit Anchoring**  
   Publishes daily SHA-256 roots of logs and benchmark results into a Matrix "transparency" room and mints them as `CIRIS-AuditRoot` credentials.

---

## 3  API Endpoints

All endpoints are under the `/api/v1/` prefix unless otherwise noted. Most require JWT authentication (see Authentication section).

**Core Endpoints:**

- **GET** `/api/v1/health`  
  Health check, returns status and public key.
- **GET** `/metrics`  
  Prometheus metrics (public, no auth).

**Benchmarks (HE-300 & SimpleBench):**
- **POST** `/api/v1/benchmarks/run`  
  Start a HE-300 benchmark run. Returns `job_id`.
- **GET** `/api/v1/benchmarks/results/{job_id}`  
  Get signed HE-300 benchmark results for a job.
- **GET** `/api/v1/benchmarks/he300`  
  List all HE-300 scenarios (content).
- **POST** `/api/v1/simplebench/run`  
  Start a SimpleBench run. Returns `job_id`.
- **GET** `/api/v1/simplebench/results/{job_id}`  
  Get SimpleBench results for a job.
- **GET** `/api/v1/benchmarks/simplebench`  
  List all SimpleBench scenarios (content).

**WBD (Wisdom-Based Deferral) & WA (Wise Authority):**
- **POST** `/api/v1/wbd/submit`  
  Submit a deferral package (agent → WA queue).
- **GET** `/api/v1/wbd/tasks`  
  List WBD tasks (filters: `state`, `since`).
- **POST** `/api/v1/wbd/tasks/{id}/resolve`  
  Resolve a WBD task (`approve`/`reject`).
- **GET** `/wa/active_tasks`  
  (Legacy) List all active tasks.
- **GET** `/wa/completed_actions`  
  (Legacy) List all completed actions.
- **POST** `/wa/defer`  
  (Legacy) Create a new task.
- **POST** `/wa/reject`  
  (Legacy) Reject a task.

**WA Actions & Memory:**
- **POST** `/api/v1/wa/action`  
  Execute a DMA action (`listen`, `useTool`, `speak`).
- **POST** `/api/v1/wa/memory`  
  Manage memory (`learn`, `remember`, `forget`).
- **POST** `/api/v1/wa/thought`  
  Submit a thought request (DMA reasoning).

**DID & Authentication:**
- **POST** `/api/v1/did/issue`  
  Issue a new DID and JWT token.
- **POST** `/api/v1/did/verify`  
  Verify a DID or credential.
- **POST** `/api/v1/auth/token`  
  Obtain JWT token (login).

**Matrix Integration:**
- **POST** `/api/v1/matrix/token`  
  Issue a Matrix access token for a DID.

**Agent Events:**
- **POST** `/api/v1/agent/events`  
  Agents push Task/Thought/Action events.
- **GET** `/api/v1/agent/events`  
  List all agent events.
- **DELETE** `/api/v1/agent/events/{event_id}`  
  Delete an agent event.
- **PATCH** `/api/v1/agent/events/{event_id}/archive`  
  Archive/unarchive an agent event.

**Audit:**
- **GET** `/api/v1/audit/logs`  
  Stream ND-JSON audit entries (query: `type`, `from`, `to`).

**Ollama (Local LLM):**
- **GET** `/api/v1/ollama-models`  
  List available Ollama models (for local LLM inference).



---

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

## Deployment

**Security Note:** For production deployments, ensure that the application is served over HTTPS only and that HSTS (HTTP Strict Transport Security) is enabled to enhance security. This is typically handled at the deployment level (e.g., via a reverse proxy like Nginx or a load balancer).

---



#### Authentication

- JWT-based route protection added using FastAPI middleware
- Token issued via `/api/v1/did/issue`
- All sensitive endpoints require `Authorization: Bearer <token>`

---


---

#### Ethical Pipeline (HE-300/EEE)

- Core HE-300 benchmark logic included
- Benchmark runs triggered via `/api/v1/benchmarks/run`
- Results are saved and accessible via `/status/{id}` and `/results/{id}`
- Placeholder inference logic is located in `utils/inference.py`

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

#### Frontend Interface for EEE (Phase 1 Complete, Phase 3 Enhanced)

A full offline-ready interface for Wise Authorities (WAs) has been developed and added to the repo at `frontend_eee/main.py`. Initially built as a Tkinter-based GUI in Phase 1, it has been upgraded in Phase 3 to a Streamlit web application for better usability and integration with the backend. The frontend now includes the following panels:
  - **Deferral Inbox**: Review and take action on ponder, reject, and defer requests, with a form to submit new deferral requests directly to the backend.
  - **DMA Actions Panel**: Trigger actions such as listen, useTool, and speak, integrated with the backend API.
  - **Ethical Benchmark Simulation**: Interface to select and run benchmarks, displaying results from the backend.

The Streamlit interface runs on `http://localhost:8501` and connects to the backend API at `http://localhost:8000/api/v1`, allowing real-time interaction with CIRISNode functionalities.

🐳 Docker Integration (Phase 2 Ready)

This frontend is now containerized and integrated into the `docker-compose.yml` file alongside the backend FastAPI app. Running both together enables real-time local testing and future backend binding. To launch:

```bash
docker-compose up --build
```

Then visit:
  - **Frontend UI**: `http://localhost:8501`
  - **Backend API**: `http://localhost:8000/docs`

---

### 🛠 Setup Instructions

This section provides detailed, step-by-step instructions to set up and run CIRISNode on your local machine or in a Docker container. Follow these steps carefully to ensure a successful setup.

#### Prerequisites

- **Python 3.10+**: Ensure Python 3.10 or higher is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Required to clone the repository. Install from [git-scm.com](https://git-scm.com/downloads).
- **Docker**: Optional, for containerized setup. Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).
- **Virtual Environment**: Recommended for isolating project dependencies.
- **Streamlit**: Required for the frontend web application. Install via pip if running locally.

#### Step 1: Clone the Repository

```bash
git clone cirisai/cirisnode  # As per FSD
cd cirisnode
```

#### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment to manage project dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

#### Step 3: Install Dependencies

Install the required Python packages listed in `requirements.txt` for the backend, and additional packages for the frontend.

```bash
pip install -r requirements.txt
pip install streamlit
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory with the necessary environment variables. Use the following template as a starting point:

TODO: CLEAN UP ENV VARIABLES

#### Step 5: Run the Server Locally

To run the FastAPI server locally, you need to export the required environment variables and use `uvicorn` to start the server. Use the following command:

```bash
export ENVIRONMENT='dev' && export JWT_SECRET='temporary_secret' && uvicorn cirisnode.main:app --reload --port 8000
```

- **`ENVIRONMENT='dev'`**: Sets the environment to development mode.
- **`JWT_SECRET='temporary_secret'`**: Sets the secret key for JWT authentication.
- **`uvicorn cirisnode.main:app --reload --port 8000`**: Starts the FastAPI server with auto-reload enabled on port 8000.

Once the server is running:
- Access the health check endpoint at `http://localhost:8000/api/v1/health` to confirm the server is operational (should return `{"status": "ok", "message": "Service is healthy", "timestamp": "2025-05-08T14:52:00Z"}`).
- Explore the API documentation at `http://localhost:8000/docs` (available in `dev` or `test` environments).

#### Step 6: Run the Streamlit Frontend Locally

To run the Streamlit frontend application, use the following command in a separate terminal:

```bash
export ENVIRONMENT='dev' && streamlit run frontend_eee/main.py
```

- **`ENVIRONMENT='dev'`**: Ensures the frontend connects to the development backend.
- The frontend will run on `http://localhost:8501`.
- Use the web interface to interact with CIRISNode functionalities, such as submitting deferral requests and managing benchmarks.

#### Step 7: Run the Test Suite Locally

Ensure your environment is set to `test` by setting `ENVIRONMENT=test` in your `.env` file or by using environment variables in the command. Install test dependencies if not already installed, then run the tests.

```bash
export JWT_SECRET='temporary_secret' && pytest tests/ -v
```

- Tests cover health checks, JWT authentication, benchmark workflows, DID issuance/verification, and more.
- Ensure `JWT_SECRET` is set to enable JWT authentication for protected routes during testing.

#### Step 8: Run Using Docker (Optional)

For a containerized setup, use Docker Compose to build and run CIRISNode.

```bash
docker compose up --build # For local development as per FSD
```

- Maps port 8000 on your host to port 8000 in the container.
- Uses the `.env` file for environment variables.
- Access the health check at `http://localhost:8000/api/v1/health`.

3. **View Container Logs**

```bash
docker logs cirisnode
```

4. **Stop the Container**

```bash
docker stop cirisnode
docker rm cirisnode
```

#### Step 9: Run Tests in Docker (Optional)

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

#### Step 10: Export OpenAPI Specification

If you want to save the OpenAPI specification for documentation or client generation:

```bash
curl http://localhost:8000/openapi.json > docs/api-spec/openapi.json
```

- Ensure the server is running on port 8000.
- The OpenAPI JSON will be saved to `docs/api-spec/openapi.json`.

---

### Errors and Troubleshooting

- **Connection Reset by Peer or "Not Found" Error when accessing http://localhost:8000/api/v1/health**: This error occurs if the server is not running or if you are trying to access the wrong port. Ensure the server is running on `http://localhost:8000` by using the command `export JWT_SECRET='temporary_secret' && uvicorn cirisnode.main:app --reload --port 8000`. If using Docker, verify the port mapping with `-p 8000:8000` in your `docker run` command. If the issue persists, check if the server or container is running with `ps aux | grep uvicorn` or `docker ps`, and restart if necessary.

- **Docker Build Fails with "No such file or directory: 'requirements.txt'"**: This happens if `requirements.txt` is missing or not in the project root. Generate it by running `pip freeze > requirements.txt` in your virtual environment before building the image. Ensure the file is committed to the repository if cloning from GitHub.

- **Unable to Access API Endpoints**: If endpoints return errors or are inaccessible:
  - Confirm the server is running (`ps aux | grep uvicorn` or `docker ps` for containers).
  - Check logs for startup errors (`docker logs <container_id>` if using Docker).
  - Verify the `.env` file exists and contains required variables like `JWT_SECRET`, or use `export JWT_SECRET='temporary_secret'` in the command. Ensure `--env-file .env` is used in `docker run` commands.
  - Test the health endpoint at `http://localhost:8000/api/v1/health`. A response of `{"status": "ok", "message": "Service is healthy", "timestamp": "2025-05-08T14:52:00Z"}` indicates the server is operational.
  - Access the interactive Swagger UI at `http://localhost:8000/docs` to explore and test endpoints directly from a browser (available in `dev` or `test` environments). Note that some endpoints require authentication headers.

- **Test Failures Due to Environment Configuration**: If tests fail with authentication errors, ensure `JWT_SECRET` is set as an environment variable when running `pytest`. This enables JWT authentication for protected routes during testing.


- **General Dependency Issues**: If `pip install` fails or dependencies conflict, ensure you're using Python 3.10+ and a clean virtual environment. Remove and recreate the virtual environment if needed (`rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`).

- **Streamlit App Not Connecting to Backend**: If the Streamlit app at `http://localhost:8501` fails to connect to the backend, ensure the server is running on `http://localhost:8000`. Check for errors in the Streamlit interface and server logs. Restart both the server and Streamlit app if necessary.

- **SQLAlchemy Errors in Tests**: If you encounter SQLAlchemy errors related to textual SQL expressions, ensure you're using the `text()` function from `sqlalchemy.sql` to wrap all SQL queries. For example, use `db.execute(text("SELECT * FROM active_tasks"))` instead of `db.execute("SELECT * FROM active_tasks")`.

For additional help, check the GitHub repository issues or contact the project maintainers.

---

### 🧪 Comprehensive Test Suite Guide

The CIRISNode project includes a robust test suite to ensure the reliability, security, and functionality of the system. This guide provides an overview of the test suite, a breakdown of each test file, and instructions for editing or adding tests.

---

#### Overview of the Test Suite

The test suite is designed to:
- Validate the functionality of all API endpoints.
- Ensure proper integration between components (e.g., backend, Matrix, JWT).
- Verify edge cases and error handling.
- Maintain system reliability during updates or new feature additions.

Tests are located in the `tests/` directory and are executed using `pytest`. The suite includes unit tests, integration tests, and functional tests.

---

#### Breakdown of Test Files


3. **`tests/test_apply.py`**
   - **Purpose**: Tests the `/apply` endpoints for graph updates (e.g., ENV_GRAPH, ID_GRAPH).
   - **Key Tests**:
     - Valid graph updates.
     - Invalid graph types or missing headers.
   - **Why It's Important**: Ensures that graph updates are applied correctly and securely.

4. **`tests/test_auth.py`**
   - **Purpose**: Tests authentication mechanisms, including JWT issuance and validation.
   - **Key Tests**:
     - JWT issuance for blessed and non-blessed DIDs.
     - Invalid JWTs or missing headers.
   - **Why It's Important**: Ensures that only authorized users can access protected endpoints.

5. **`tests/test_benchmarks.py`**
   - **Purpose**: Tests the `/benchmarks` endpoints for running and retrieving HE-300 benchmarks.
   - **Key Tests**:
     - Valid benchmark runs.
     - Missing or invalid parameters.
   - **Why It's Important**: Validates the core benchmarking functionality of the system.

6. **`tests/test_deferral.py`**
   - **Purpose**: Tests the `/wa/deferral` endpoint for handling deferral requests.
   - **Key Tests**:
     - Valid deferral submissions.
     - Invalid deferral types or missing parameters.
   - **Why It's Important**: Ensures that deferral requests are processed correctly and invalid requests are rejected.

8. **`tests/test_health.py`**
   - **Purpose**: Tests the `/health` endpoint for system health checks.
   - **Key Tests**:
     - Valid health check responses.
     - Missing or invalid headers.
   - **Why It's Important**: Provides a quick way to verify system availability.

9. **`tests/test_jwt_auth.py`**
   - **Purpose**: Tests JWT issuance and access to protected endpoints.
   - **Key Tests**:
     - Valid and invalid JWTs.
     - Access to protected endpoints with and without valid tokens.
   - **Why It's Important**: Ensures that JWT-based authentication is functioning correctly.


14. **`tests/test_wa.py`**
    - **Purpose**: Tests the `/wa` endpoints for ticket submissions and deferral handling.
    - **Key Tests**:
      - Valid ticket submissions.
      - Valid and invalid deferral requests.
    - **Why It's Important**: Ensures that WA-related workflows are functioning correctly.

---

#### How to Edit Tests

1. **Locate the Test File**: Identify the relevant test file in the `tests/` directory.
2. **Understand the Test Structure**: Review existing tests to understand the structure and conventions.
3. **Add or Modify Tests**:
   - Use `pytest` fixtures for setup and teardown.
   - Follow the naming conventions for test functions (`test_*`).
   - Use `assert` statements to validate expected outcomes.
4. **Run the Tests**: Execute the test suite using `pytest` to verify your changes.

---

#### Why the Tests Are Important

The test suite is a critical component of the CIRISNode project. It ensures:
- **Reliability**: Verifies that the system behaves as expected under various conditions.
- **Security**: Validates authentication, authorization, and data integrity.
- **Maintainability**: Provides a safety net for future updates or feature additions.
- **Compliance**: Ensures adherence to ethical and technical standards.

By maintaining a comprehensive and up-to-date test suite, we can confidently deliver a robust and secure system.

---

### 🧪 Test Suite Coverage

All test files are located in `tests/` and cover:
- `/health` endpoint
- JWT issuance and protection
- Matrix message sending
- Benchmark run and result lifecycle (HE-300)
- WA ticket submission and tracking, including deferral submissions
- Async support (with `pytest-asyncio`)
- Config loading from `.env`


### 🧵 Final Word

CIRISNode is now fully operational in dev/test environments with full API, Matrix, and testing infrastructure, supporting future integration into the CIRISAgent client ecosystem and Hyperledger Aries stack. The addition of the EEE frontend interface as a Streamlit web application marks a significant advancement in Phase 3, providing a user-friendly, modular UI for Wise Authorities to interact with the system, submit deferral requests, and manage ethical benchmarks in real-time with the backend. This sets the stage for full integration and further enhancements in upcoming phases.

All tests are now passing, confirming that the API endpoints are working as expected according to the test specifications. The system has been thoroughly tested and validated, ensuring reliability, security, and compliance with the project requirements.

– Bradley Matera, May 2025
