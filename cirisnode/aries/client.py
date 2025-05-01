async def issue_credential(payload: dict) -> dict:
    """Mock function to issue a credential."""
    return {"vc": "mock-vc", "status": "issued"}

async def verify_credential(vc: dict) -> dict:
    """Mock function to verify a credential."""
    return {"valid": True}
