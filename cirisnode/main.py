from fastapi import FastAPI, Request, Depends
from cirisnode.api.health.routes import health_check as ciris_health_check
from cirisnode.api.wbd.routes import wbd_router # Assuming wbd_router is defined in wbd/routes.py
from cirisnode.api.audit.routes import audit_router # Assuming audit_router is defined in audit/routes.py
from cirisnode.api.agent.routes import agent_router # Assuming agent_router is defined in agent/routes.py
from cirisnode.api.benchmarks.routes import benchmarks_router, simplebench_router
from eee.api.main import startup_event, shutdown_event, log_requests # Assuming these are still relevant
# from cirisnode.api.auth.dependencies import verify_token # Security is out of scope for now

app = FastAPI(title="CIRISNode", version="1.2.0")

# Lifecycle events
@app.on_event("startup")
async def on_startup():
    # Placeholder for actual startup logic from eee.api.main or cirisnode specific
    # await startup_event()
    print("CIRISNode has started.")
    # Initialize database, load models, etc.

@app.on_event("shutdown")
async def on_shutdown():
    # Placeholder for actual shutdown logic
    # await shutdown_event()
    print("CIRISNode is shutting down.")

# Middleware (if still needed from eee)
# @app.middleware("http")
# async def log_requests_middleware(request: Request, call_next):
#     return await log_requests(request, call_next)

@app.get("/")
async def read_root():
    return {"message": "Welcome to CIRISNode v1.2"}

# Include routers from different modules
app.include_router(ciris_health_check, prefix="/api/v1") # Assuming health_check is a router or needs to be wrapped
app.include_router(benchmarks_router)
app.include_router(simplebench_router)
app.include_router(wbd_router, prefix="/api/v1/wbd", tags=["wbd"]) # Ensure wbd_router uses this prefix
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"]) # Ensure audit_router uses this prefix
app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent_events"]) # Ensure agent_router uses this prefix

# Placeholder for /metrics endpoint
@app.get("/metrics")
async def get_metrics():
    # In a real application, this would return Prometheus metrics
    return {"metrics": "prometheus_metrics_placeholder"}

# Example of how to integrate existing individual route functions if they are not part of a router
# from cirisnode.api.wbd.routes import get_wbd_tasks_route_function # Example name
# app.add_api_route("/api/v1/wbd/tasks", get_wbd_tasks_route_function, methods=["GET"], tags=["wbd"])
