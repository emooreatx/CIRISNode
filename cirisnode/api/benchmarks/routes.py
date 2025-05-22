from fastapi import APIRouter, HTTPException, Depends
from cirisnode.database import get_db
import json
import os
import requests

benchmarks_router = APIRouter(prefix="/api/v1/benchmarks", tags=["benchmarks"])
simplebench_router = APIRouter(prefix="/api/v1/simplebench", tags=["simplebench"])

@simplebench_router.post("/run-sync")
async def run_simplebench_sync(payload: dict, db=Depends(get_db)):
    """
    Run a SimpleBench job synchronously.
    """
    # Load the SimpleBench scenarios from the JSON file
    json_path = os.path.join("ui", "public", "simple_bench_public.json")
    try:
        with open(json_path, "r") as f:
            simple_bench_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="SimpleBench data file not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse SimpleBench data file.")

    # Extract the eval_data
    scenarios = simple_bench_data.get("eval_data", [])
    if not scenarios:
        raise HTTPException(status_code=500, detail="No scenarios found in SimpleBench data.")

    # Filter scenarios based on the provided scenario_ids
    scenario_ids = payload.get("scenario_ids", [])
    filtered_scenarios = [s for s in scenarios if str(s["question_id"]) in scenario_ids]

    # Determine the provider and model
    provider = payload.get("provider")
    model = payload.get("model")
    if not provider or not model:
        raise HTTPException(status_code=400, detail="Provider and model must be specified.")

    # Generate results by querying the AI model
    results = []
    for scenario in filtered_scenarios:
        prompt = scenario["prompt"]
        try:
            if provider == "openai":
                # Query OpenAI API
                response = requests.post(
                    "https://api.openai.com/v1/completions",
                    headers={
                        "Authorization": f"Bearer {payload.get('apiKey')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "prompt": prompt,
                        "max_tokens": 100,
                        "temperature": 0.7
                    }
                )
                response.raise_for_status()
                ai_response = response.json().get("choices", [{}])[0].get("text", "").strip()
            elif provider == "ollama":
                # Query Ollama API
                response = requests.post(
                    f"http://127.0.0.1:11434/api/generate",
                    json={"model": model, "prompt": prompt}
                )
                response.raise_for_status()
                # Debugging: Log the raw response
                # Log the raw response to a file for debugging
                # Process streaming JSON response
                ai_response = ""
                for line in response.iter_lines():
                    if line.strip():
                        try:
                            json_line = json.loads(line)
                            ai_response += json_line.get("response", "")
                        except json.JSONDecodeError:
                            continue
                ai_response = ai_response.strip()
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to query {provider}: {str(e)}")

        # Determine if the response matches the expected answer
        passed = ai_response.lower() == scenario["answer"].lower()

        # Append the result
        results.append({
            "scenario_id": str(scenario["question_id"]),
            "prompt": prompt,
            "response": ai_response,
            "expected_answer": scenario["answer"],
            "model_used": model,
            "passed": passed
        })

    return {
        "status": "success",
        "results": results
    }

# ... rest of the file unchanged ...
