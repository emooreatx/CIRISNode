from pydantic import BaseModel
from typing import Optional

class DIDIssueRequest(BaseModel):
    did: str
    public_key: Optional[str]

class DIDVerifyRequest(BaseModel):
    did: str
    public_key: str
