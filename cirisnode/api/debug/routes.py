from fastapi import APIRouter, Request

debug_router = APIRouter(tags=["debug"], prefix="/api/v1")

@debug_router.post("/debug")
async def debug_endpoint(request: Request):
    body = await request.json()
    headers = dict(request.headers)
    return {"headers": headers, "body": body}
