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
    # Temporarily bypass authentication for testing purposes
    return await call_next(request)
    # if request.url.path in ["/api/v1/health", "/api/v1/did/issue", "/api/v1/did/verify"]:
    #     return await call_next(request)  # Skip authentication for health check, token issuance, and verification
    # auth_header = request.headers.get("Authorization")
    # if not auth_header or not auth_header.startswith("Bearer "):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    # token = auth_header.split("Bearer ")[1]
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    #     request.state.user = payload
    # except jwt.ExpiredSignatureError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    # except jwt.InvalidTokenError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # return await call_next(request)

app.middleware("http")(verify_token)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

app.include_router(did_router, prefix="/api/v1/did")
app.include_router(benchmarks_router, prefix="/api/v1/benchmarks")
app.include_router(wa_router, prefix="/api/v1/wa")
