from pydantic import BaseModel
from typing import List

class BenchmarkPrompt(BaseModel):
    id: str
    prompt: str

class BenchmarkResult(BaseModel):
    id: str
    response: str
    timestamp: str
