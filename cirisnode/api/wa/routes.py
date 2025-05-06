from fastapi import APIRouter, Response, status, Request, Depends, HTTPException
import uuid
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

wa_router = APIRouter(tags=["wa"])

async def get_user_metadata(request: Request):
    user = getattr(request.state, 'user', {"sub": "unknown", "did": "did:mock:unknown"})
    did = request.headers.get("X-DID", user.get("did", "did:mock:unknown"))
    return {
        "did": did,
        "timestamp": datetime.utcnow().isoformat()
    }

@wa_router.post("/authenticate")
async def authenticate():
    from cirisnode.api.did.routes import SECRET_KEY, ALGORITHM
    from datetime import datetime, timedelta
    import jwt
    
    # Use a more realistic mocked user ID
    mocked_user_id = "wa_user_001"
    mocked_did = "did:peer:wa_user_001"
    payload = {
        "sub": mocked_user_id,
        "did": mocked_did,
        "role": "agent",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Authentication token issued for user {mocked_user_id}, DID: {mocked_did}")
    return {
        "status": "authenticated",
        "token": token,
        "user_id": mocked_user_id,
        "did": mocked_did,
        "message": "Token valid for 1 hour"
    }

@wa_router.get("/profile/{user_id}")
async def get_profile(user_id: str, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    logger.info(f"Profile requested for user {user_id}, DID: {metadata['did']}")
    return {
        "user_id": user_id,
        "profile": {
            "name": "Mock User",
            "email": f"{user_id}@example.com",
            "role": "agent",
            "last_active": "2023-05-05T10:30:00Z",
            "status": "active"
        },
        "did": metadata["did"],
        "timestamp": metadata["timestamp"]
    }

@wa_router.post("/logout")
async def logout(metadata: Dict[str, Any] = Depends(get_user_metadata)):
    logger.info(f"User logout requested, DID: {metadata['did']}")
    return {
        "status": "logged out",
        "message": "Session terminated successfully",
        "did": metadata["did"],
        "timestamp": metadata["timestamp"]
    }

@wa_router.post("/ticket")
async def submit_ticket(response: Response, request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    ticket_id = str(uuid.uuid4())
    # Mocked ticket submission logic
    logger.info(f"Ticket submitted with ID {ticket_id}, DID: {metadata['did']}")
    return {
        "ticket_id": ticket_id,
        "status": "submitted",
        "message": "Ticket received and queued for processing",
        "submitted_at": datetime.utcnow().isoformat(),
        "did": metadata["did"],
        "timestamp": metadata["timestamp"]
    }

@wa_router.get("/status/{ticket_id}")
async def check_ticket_status(ticket_id: str, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    # Mocked status check logic
    logger.info(f"Status check for ticket {ticket_id}, DID: {metadata['did']}")
    return {
        "ticket_id": ticket_id,
        "status": "processing",
        "message": "Ticket is being processed",
        "last_updated": datetime.utcnow().isoformat(),
        "did": metadata["did"],
        "timestamp": metadata["timestamp"]
    }

@wa_router.post("/run")
async def run_agent_request(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    import httpx
    try:
        # Get input from agent request
        data = await request.json()
        query = data.get("text", "Test query to Ollama")
        logger.info(f"Agent request received with query: {query}, DID: {metadata['did']}")
        
        # Send query to Ollama (assuming it's running on default port 11434)
        async with httpx.AsyncClient() as client:
            ollama_response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral:latest",  # Using available model
                    "prompt": query,
                    "stream": False
                },
                timeout=30.0
            )
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                response_text = result.get("response", "No response from Ollama")
                logger.info(f"Ollama response received for query: {query}, DID: {metadata['did']}")
                return {
                    "status": "success",
                    "decision": response_text,
                    "response_time": result.get("response_time", "unknown"),
                    "model_used": "mistral:latest",
                    "did": metadata["did"],
                    "timestamp": metadata["timestamp"]
                }
            else:
                error_msg = f"Ollama request failed with status {ollama_response.status_code}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "decision": error_msg,
                    "error_code": ollama_response.status_code,
                    "did": metadata["did"],
                    "timestamp": metadata["timestamp"]
                }
    except Exception as e:
        error_msg = f"Error connecting to Ollama: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "decision": error_msg,
            "error_detail": "Connection or processing error",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }

@wa_router.post("/action")
async def take_action(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        action_type = data.get("action_type")
        if action_type not in ["listen", "useTool", "speak"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action type. Must be 'listen', 'useTool', or 'speak'.")
        
        decision_id = str(uuid.uuid4())
        logger.info(f"TAKE ACTION: {action_type} by DID: {metadata['did']}, Decision ID: {decision_id}")
        return {
            "status": "success",
            "decision_id": decision_id,
            "action": action_type,
            "handler": "TAKE_ACTION",
            "message": f"Action {action_type} processed and queued for graph update",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error processing TAKE ACTION: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing action: {str(e)}")

@wa_router.post("/deferral")
async def wise_deferral(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        deferral_type = data.get("deferral_type")
        if deferral_type != "defer":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only 'defer' is handled by the backend.")
        
        reason = data.get("reason", "No reason provided")
        target_object = data.get("target_object", "N/A")
        decision_id = str(uuid.uuid4())
        logger.info(f"WISE DEFERRAL: {deferral_type} by DID: {metadata['did']}, Reason: {reason}, Decision ID: {decision_id}")
        return {
            "status": "success",
            "decision_id": decision_id,
            "action": deferral_type,
            "handler": "WISE_DEFERRAL",
            "reason": reason,
            "target_object": target_object,
            "message": f"Deferral {deferral_type} processed and logged",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error processing WISE DEFERRAL: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing deferral: {str(e)}")

@wa_router.post("/memory")
async def handle_memory(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        memory_action = data.get("memory_action")
        if memory_action not in ["learn", "remember", "forget"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid memory action. Must be 'learn', 'remember', or 'forget'.")
        
        content = data.get("content", "N/A")
        decision_id = str(uuid.uuid4())
        logger.info(f"MEMORY: {memory_action} by DID: {metadata['did']}, Decision ID: {decision_id}")
        return {
            "status": "success",
            "decision_id": decision_id,
            "action": memory_action,
            "handler": "MEMORY",
            "content": content,
            "message": f"Memory action {memory_action} processed",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error processing MEMORY action: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing memory action: {str(e)}")

@wa_router.post("/thought")
async def submit_thought(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        thought_content = data.get("content", "No content provided")
        dma_type = data.get("dma_type", "CommonSense")  # Default to CommonSense if not specified
        if dma_type not in ["CommonSense", "Principled", "DomainSpecific"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid DMA type. Must be 'CommonSense', 'Principled', or 'DomainSpecific'.")
        
        thought_id = str(uuid.uuid4())
        logger.info(f"THOUGHT submitted by DID: {metadata['did']}, Assigned to DMA: {dma_type}, Thought ID: {thought_id}")
        return {
            "status": "success",
            "thought_id": thought_id,
            "content": thought_content,
            "dma_type": dma_type,
            "message": f"Thought queued for processing in {dma_type} DMA",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error processing THOUGHT: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing thought: {str(e)}")
