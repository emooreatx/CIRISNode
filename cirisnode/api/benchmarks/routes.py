from fastapi import APIRouter, HTTPException, Depends
from cirisnode.database import get_db
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from cirisnode.celery_tasks import run_he300_scenario_task, run_simplebench_task # Assuming celery tasks are defined here

benchmarks_router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])
simplebench_router = APIRouter(prefix="/api/v1/simplebench", tags=["simplebench"])

class BenchmarkRunRequest(BaseModel):
    scenario_id: Optional[str] = None
    chaos_level: Optional[float] = None

class SimpleBenchRequest(BaseModel):
    scenario_ids: list[str]
    provider: str
    model: str
    apiKey: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str

from typing import List

class BenchmarkResultResponse(BaseModel):
    job_id: str
    status: str
    results: Optional[List[Dict[str, Any]]] = None  # List of result dicts

# Placeholder for storing job statuses and results - in a real app, this would be a database or a persistent store
job_store: Dict[str, Dict[str, Any]] = {}

@benchmarks_router.post("/run", response_model=JobResponse)
async def run_he300_benchmark(request: BenchmarkRunRequest, db=Depends(get_db)):
    """
    Run any or all of 29,973 HE-300 scenarios asynchronously; store signed result bundle.
    Body `{scenario_id?, chaos_level?}` → returns `job_id`.
    """
    import json as pyjson
    job_id = str(uuid.uuid4())
    # Simulate async task execution with Celery
    # In a real app, you'd call: run_he300_scenario_task.delay(job_id, request.scenario_id, request.chaos_level)
    job_store[job_id] = {"status": "pending", "type": "he300", "results": None}
    # Persist job in jobs table
    try:
        conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
        conn.execute(
            """
            INSERT INTO jobs (id, type, status, started_at, finished_at, results_url, results_json)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL, NULL, ?)
            """,
            (job_id, "he300", "pending", pyjson.dumps({}))
        )
        conn.commit()
        print(f"HE-300 job {job_id} written to jobs table.")
    except Exception as e:
        print(f"ERROR: Failed to write HE-300 job {job_id} to jobs table: {e}")
    return JobResponse(job_id=job_id)

@benchmarks_router.get("/results/{job_id}", response_model=BenchmarkResultResponse)
async def get_he300_benchmark_results(job_id: str, db=Depends(get_db)):
    """
    Signed HE-300 results bundle.
    """
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    cur = conn.execute(
        "SELECT status, results_json FROM jobs WHERE id = ? AND type = 'he300'",
        (job_id,)
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="HE-300 Benchmark job not found")
    status, results_json = row
    import json as pyjson
    results = pyjson.loads(results_json) if results_json else []
    return BenchmarkResultResponse(job_id=job_id, status=status, results=results)

from fastapi import Depends

@simplebench_router.post("/run-sync")
async def run_simplebench_sync(request: SimpleBenchRequest, db=Depends(get_db)):
    """
    Run SimpleBench synchronously with selected scenarios and store results for job-based retrieval.
    """
    from cirisnode.api.llm.routes import test_llm_connection
    from cirisnode.api.llm.routes import LLMTestRequest
    import json

    # Load scenarios data
    with open('ui/public/simple_bench_public.json') as f:
        scenarios_data = json.load(f)

    results = []

    # Get selected scenarios
    selected_scenarios = [
        s for s in scenarios_data['eval_data']
        if str(s['question_id']) in request.scenario_ids
    ]

    # Run tests for each selected scenario
    for scenario in selected_scenarios:
        try:
            llm_response = await test_llm_connection(LLMTestRequest(
                provider=request.provider,
                prompt=scenario['prompt'],
                model=request.model
            ))

            print(f"DEBUG: LLM raw response for scenario {scenario['question_id']}: {llm_response}")

            # Prefer the "message" field if present, else fallback to string
            if isinstance(llm_response, dict) and "message" in llm_response:
                llm_output = llm_response["message"]
            else:
                llm_output = str(llm_response)
            # Extract the first answer letter (A-F) from the LLM output
            import re
            match = re.search(r"\b([A-F])\b", llm_output)
            llm_choice = match.group(1) if match else ""
            passed = llm_choice.upper() == scenario['answer'].strip().upper()
            results.append({
                "scenario_id": str(scenario['question_id']),
                "model_used": request.model,
                "prompt": scenario['prompt'],
                "response": llm_output,
                "expected_answer": scenario['answer'],
                "passed": passed
            })

        except Exception as e:
            results.append({
                "scenario_id": str(scenario['question_id']),
                "model_used": request.model,
                "prompt": scenario['prompt'],
                "response": f"Error: {str(e)}",
                "expected_answer": scenario['answer'],
                "passed": False
            })

    # Store results in job_store for job-based retrieval
    import json as pyjson
    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "completed",
        "type": "simplebench",
        "results": results
    }
    # Persist job in jobs table
    try:
        conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
        conn.execute(
            """
            INSERT INTO jobs (id, type, status, started_at, finished_at, results_url, results_json)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, ?)
            """,
            (job_id, "simplebench", "completed", pyjson.dumps(results))
        )
        conn.commit()
        print(f"Job {job_id} written to jobs table.")
    except Exception as e:
        print(f"ERROR: Failed to write job {job_id} to jobs table: {e}")

    # Write audit log
    try:
        from cirisnode.utils.audit import write_audit_log
        conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
        write_audit_log(
            db=conn,
            actor=None,  # Optionally set from auth context
            event_type="simplebench_run",
            payload={"job_id": job_id, "scenario_ids": request.scenario_ids},
            details={"results": results}
        )
    except Exception as e:
        print(f"WARNING: Failed to write audit log for simplebench_run: {e}")

    return {"job_id": job_id, "results": results}

@simplebench_router.get("/results/{job_id}", response_model=BenchmarkResultResponse)
async def get_simplebench_results(job_id: str, db=Depends(get_db)):
    """
    SimpleBench results.
    """
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    cur = conn.execute(
        "SELECT status, results_json FROM jobs WHERE id = ? AND type = 'simplebench'",
        (job_id,)
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="SimpleBench job not found")
    status, results_json = row
    import json as pyjson
    results = pyjson.loads(results_json) if results_json else []
    return BenchmarkResultResponse(job_id=job_id, status=status, results=results)
