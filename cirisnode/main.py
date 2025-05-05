from fastapi import FastAPI, Request, HTTPException, status
from cirisnode.api.benchmarks.routes import benchmarks_router
from cirisnode.api.did.routes import did_router
from cirisnode.api.wa.routes import wa_router
import jwt
from cirisnode.api.did.routes import SECRET_KEY, ALGORITHM

import os
app = FastAPI(
    title="CIRISNode",
    docs_url=None if os.getenv("ENVIRONMENT", "dev") == "prod" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT", "dev") == "prod" else "/redoc",
    openapi_url=None if os.getenv("ENVIRONMENT", "dev") == "prod" else "/openapi.json"
)

async def verify_token(request: Request, call_next):
    from starlette.responses import JSONResponse
    import logging
    logger = logging.getLogger(__name__)
    
    # Debugging: Log the ENVIRONMENT variable
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'dev')}")

    # Skip authentication for health check, token issuance, verification, authenticate, and documentation endpoints
    if request.url.path in ["/api/v1/health", "/api/v1/did/issue", "/api/v1/did/verify", "/api/v1/wa/authenticate", "/openapi.json"] or \
       request.url.path.startswith(("/docs", "/redoc")):
        return await call_next(request)
    
    # Allow bypass for testing environment
    if os.getenv("ENVIRONMENT", "dev") == "test":
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid Authorization header"}
        )
    token = auth_header.split("Bearer ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expired for token: {token}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token expired"}
        )
    except jwt.InvalidTokenError:
        logger.warning(f"Invalid token received: {token}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error during token verification"}
        )
    return await call_next(request)

app.middleware("http")(verify_token)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

app.include_router(did_router, prefix="/api/v1/did")
app.include_router(benchmarks_router, prefix="/api/v1/benchmarks")
app.include_router(wa_router, prefix="/api/v1/wa")
