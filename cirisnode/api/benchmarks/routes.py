from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import os
import jwt
from datetime import datetime

benchmarks_router = APIRouter()

# Load environment variables for authorization
ALLOWED_BLESSED_DIDS = set(os.getenv("ALLOWED_BLESSED_DIDS", "").split(","))
ALLOWED_BENCHMARK_IPS = os.getenv("ALLOWED_BENCHMARK_IPS", "").split(",")
ALLOWED_BENCHMARK_TOKENS = set(os.getenv("ALLOWED_BENCHMARK_TOKENS", "").split(","))
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

# Matrix logging configuration
MATRIX_LOGGING_ENABLED = os.getenv("MATRIX_LOGGING_ENABLED", "false").lower() == "true"

def logAttempt(ip: str, did: str, method: str, outcome: str):
    timestamp = datetime.now().isoformat()
    log_message = f"{timestamp} - IP: {ip}, DID/Method: {did or method}, Outcome: {outcome}"
    print(log_message)  # Console/file logging
    
    if MATRIX_LOGGING_ENABLED:
        try:
            from matrix_client.client import MatrixClient
            homeserver_url = os.getenv("MATRIX_HOMESERVER_URL")
            access_token = os.getenv("MATRIX_ACCESS_TOKEN")
            room_id = os.getenv("MATRIX_ROOM_ID")
            client = MatrixClient(homeserver_url)
            client.login_with_token(access_token)
            msg = f"{outcome == 'ALLOWED' and '✅' or '⛔'} {outcome}: {method} by {did or ip}"
            client.room_send(room_id, "m.room.message", {"msgtype": "m.text", "body": msg})
        except Exception as e:
            print(f"Matrix logging failed: {e}")

def extractBearerToken(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split("Bearer ")[1]
    return ""

def isIpAllowed(ip: str) -> bool:
    if not ip:
        return False
    for allowed_ip in ALLOWED_BENCHMARK_IPS:
        if "/" in allowed_ip:  # CIDR notation
            ip_range = allowed_ip.split("/")
            if ip.startswith(ip_range[0][:ip_range[0].rfind(".")]):
                return True
        elif ip == allowed_ip:
            return True
    return False

def verifyJwt(token: str, secret: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid token")

@benchmarks_router.post("/run")
async def run_benchmark(request: Request):
    token = extractBearerToken(request)
    client_ip = request.client.host

    # TEMP BYPASS for test mode
    if os.getenv("ENVIRONMENT") == "test":
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        TEST_ALLOWED_TOKENS = ["sk_test_abc123"]
        TEST_ALLOWED_DIDS = ["did:example:12345"]
        try:
            token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"]) if token else None
        except jwt.InvalidTokenError:
            token_data = None
        if token in TEST_ALLOWED_TOKENS or (token_data and token_data.get("did") in TEST_ALLOWED_DIDS):
            return {"message": "Benchmark run initiated", "scenario": (await request.json()).get("scenario")}

    # 1. Static token bypass (DEV only)
    if token in ALLOWED_BENCHMARK_TOKENS:
        logAttempt(client_ip, "", "static token", "ALLOWED")
        return {"message": "Benchmark run initiated", "scenario": (await request.json()).get("scenario")}

    # 2. IP allow-list bypass (DEV only)
    if isIpAllowed(client_ip):
        logAttempt(client_ip, "", "IP allow-list", "ALLOWED")
        return {"message": "Benchmark run initiated", "scenario": (await request.json()).get("scenario")}

    # 3. JWT + DID blessing check
    try:
        payload = verifyJwt(token, JWT_SECRET)
        user_did = payload.get("did")

        # STUB: static DID blessing (to be replaced by Aries VC proof)
        if user_did not in ALLOWED_BLESSED_DIDS:
            logAttempt(client_ip, user_did, "DID check", "DENIED")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: DID not blessed")

        logAttempt(client_ip, user_did, "DID check", "ALLOWED")
        return {"message": "Benchmark run initiated", "scenario": (await request.json()).get("scenario")}
    except HTTPException as e:
        logAttempt(client_ip, "", "JWT validation", "DENIED")
        raise e
    except Exception as e:
        logAttempt(client_ip, "", "JWT validation", "DENIED")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
