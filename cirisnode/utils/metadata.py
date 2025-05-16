from fastapi import Request
from datetime import datetime

async def get_user_metadata(request: Request):
    """Extract DID and timestamp metadata from the request."""
    user = getattr(request.state, 'user', {"sub": "unknown", "did": "did:mock:unknown"})
    did = request.headers.get("X-DID", user.get("did", "did:mock:unknown"))
    return {
        "did": did,
        "timestamp": datetime.utcnow().isoformat(),
    }
