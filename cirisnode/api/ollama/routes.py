from fastapi import APIRouter, HTTPException
import httpx

ollama_router = APIRouter(tags=["ollama"])

@ollama_router.get("/api/v1/ollama-models")
async def get_ollama_models():
    """
    Fetch installed Ollama models and return simplified list
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:11434/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"models": [model["name"] for model in data.get("models", [])]}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
