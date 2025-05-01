from fastapi import APIRouter, Response, status
import jwt
from datetime import datetime, timedelta
from cirisnode.aries.client import issue_credential, verify_credential

did_router = APIRouter(tags=["did"])
SECRET_KEY = "mocked-secret-key-for-development"  # Replace with secure key in production
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30

@did_router.post("/create")
async def create_did():
    return {"status": "DID created", "did": "did:example:123456"}

@did_router.get("/{did}")
async def get_did(did: str):
    return {"did": did, "details": "mocked DID details"}

@did_router.put("/{did}/update")
async def update_did(did: str):
    return {"did": did, "status": "updated"}

@did_router.post("/issue")
async def issue_did(response: Response):
    # Integration with Aries agent for DID issuance
    did = "did:aries:789012"
    payload = {"did": did}
    credential_result = await issue_credential(payload)
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    token = jwt.encode({"sub": did, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    return {"status": "DID issued", "did": did, "credential": credential_result["vc"], "token": token}

@did_router.post("/verify")
async def verify_did():
    # Integration with Aries agent for DID verification
    vc = {"vc": "mock-vc"}
    verification_result = await verify_credential(vc)
    return {"status": "DID verified", "did": "did:aries:789012", "valid": verification_result["valid"]}
