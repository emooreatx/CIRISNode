from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class DeferralRequest(BaseModel):
    did: str
    reason: Optional[str]

class RejectionRequest(BaseModel):
    did: str
    justification: str

class CorrectionRequest(BaseModel):
    original_decision_id: UUID
    correction: str

class WAEntry(BaseModel):
    id: UUID
    did: str
    action: str
    details: str
    timestamp: datetime

class DeferRequest(BaseModel):
    thought_id: str
    reason: str
    timestamp: str
