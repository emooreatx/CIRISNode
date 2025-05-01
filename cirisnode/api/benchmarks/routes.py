from fastapi import APIRouter, Response, status
from pydantic import BaseModel
import json
import os
import hashlib
from datetime import datetime

benchmarks_router = APIRouter()

class BenchmarkRequest(BaseModel):
    scenario: str
    parameters: dict = {}

def save_result(result_data: dict):
    """Save benchmark result to a local file with metadata."""
    results_dir = "./results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    timestamp = datetime.now().isoformat()
    result_id = hashlib.sha256(f"{timestamp}{result_data['scenario']}".encode()).hexdigest()[:8]
    file_path = f"{results_dir}/benchmark_{result_id}_{timestamp.replace(':', '-')}.json"
    
    # Add metadata and sign the result
    result_data.update({
        "timestamp": timestamp,
        "result_id": result_id,
        "signature": hashlib.sha256(json.dumps(result_data, sort_keys=True).encode()).hexdigest()
    })
    
    with open(file_path, "w") as f:
        json.dump(result_data, f, indent=2)
    
    return file_path

@benchmarks_router.get("/")
async def get_benchmarks():
    return {"message": "Benchmarks endpoint", "available_scenarios": ["HE-300"]}

@benchmarks_router.post("/execute")
async def execute_benchmark(request: BenchmarkRequest, response: Response):
    if request.scenario != "HE-300":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Unsupported scenario: {request.scenario}"}
    
    # Mocked execution of HE-300 suite
    result_data = {
        "scenario": request.scenario,
        "parameters": request.parameters,
        "status": "completed",
        "results": {"mocked_metric": 42.0}
    }
    
    saved_path = save_result(result_data)
    return {"message": "Benchmark executed", "result_file": saved_path, "result_id": result_data["result_id"]}

@benchmarks_router.post("/run")
async def run_benchmark(request: BenchmarkRequest, response: Response):
    if request.scenario != "HE-300":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Unsupported scenario: {request.scenario}"}
    
    # Mocked execution of benchmark
    result_data = {
        "scenario": request.scenario,
        "parameters": request.parameters,
        "status": "running",
        "run_id": "mock_run_id_" + hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:8]
    }
    
    return {"message": "Benchmark started", "run_id": result_data["run_id"]}

@benchmarks_router.get("/status/{run_id}")
async def get_benchmark_status(run_id: str):
    # Mocked status check
    return {"run_id": run_id, "status": "completed", "progress": 100}

@benchmarks_router.get("/results/{run_id}")
async def get_benchmark_results(run_id: str):
    # Mocked results retrieval
    return {
        "run_id": run_id,
        "status": "completed",
        "signed_report": {
            "results": {"mocked_metric": 42.0},
            "signature": "mocked_signature_" + hashlib.sha256(run_id.encode()).hexdigest()[:8]
        }
    }
