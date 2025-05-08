from fastapi import FastAPI
from cirisnode.api.wa.routes import wa_router
from cirisnode.api.graph.routes import graph_router
from cirisnode.api.did.routes import did_router
from cirisnode.api.benchmarks.routes import benchmarks_router

app = FastAPI()

# Include routers
app.include_router(wa_router, prefix="/api/v1/wa")
app.include_router(wa_router, prefix="/wa")  # For test_wa.py
app.include_router(graph_router, prefix="/api/v1/graph")
app.include_router(did_router, prefix="/api/v1/did")
app.include_router(benchmarks_router, prefix="/api/v1/benchmarks")

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "timestamp": "2025-05-08T14:52:00Z", "message": "Service is healthy"}
