from fastapi import APIRouter
from cirisnode.api.health.routes import router as health_router
from cirisnode.api.wbd.routes import wbd_router
from cirisnode.api.audit.routes import audit_router
from cirisnode.api.benchmarks.routes import benchmarks_router
from cirisnode.api.benchmarks.content import router as benchmarks_content_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(wbd_router)
api_router.include_router(benchmarks_router, prefix="/api/v1/benchmarks")
api_router.include_router(benchmarks_content_router, prefix="/api/v1/benchmarks")
@api_router.get("/test-api-router")  # Test route for API router
def test_api_router():
    return {"message": "API router is working"}

api_router.include_router(audit_router)
