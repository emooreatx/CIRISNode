from pydantic import BaseModel
from typing import Optional, Dict, Any

# Benchmark Models
class BenchmarkPrompt(BaseModel):
    prompt: str
    metadata: Optional[Dict[str, Any]]

class BenchmarkResult(BaseModel):
    result: str
    score: float

# WA Models
class DeferralRequest(BaseModel):
    task_id: str
    reason: str

class RejectionRequest(BaseModel):
    task_id: str
    reason: str

class CorrectionRequest(BaseModel):
    task_id: str
    correction: str

class WAEntry(BaseModel):
    entry_id: str
    content: str

class DeferRequest(BaseModel):
    task_id: str
    defer_until: str

# Ethical Guidance
class EthicalGuidance(BaseModel):
    guidance_id: str
    description: str

# Results
class Results(BaseModel):
    metrics: Dict[str, float]
    violations: Optional[Dict[str, Any]]

# Pipeline
class Pipeline(BaseModel):
    pipeline_id: str
    stages: Optional[Dict[str, Any]]

# Identity
class Identity(BaseModel):
    identity_id: str
    attributes: Dict[str, Any]
