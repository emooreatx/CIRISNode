from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import ValidationError
from cirisnode.schema.matrix_models import MatrixMessageRequest
from typing import Dict, Any, List
from datetime import datetime
from cirisnode.utils.metadata import get_user_metadata
import logging

# Setup logging
logger = logging.getLogger(__name__)

matrix_router = APIRouter(tags=["matrix"])

# In-memory storage for mock messages
matrix_messages: List[Dict[str, str]] = []

@matrix_router.post("/send")
async def send_message(request: MatrixMessageRequest, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        message_data = {
            "room_id": request.room_id,
            "token": request.token,
            "message": request.message,
            "timestamp": datetime.utcnow().isoformat(),
            "did": metadata["did"]
        }
        matrix_messages.append(message_data)
        logger.info(f"Matrix message sent to room {request.room_id} by DID: {metadata['did']}")
        print(f"Matrix message sent: {message_data}")
        return {
            "status": "success",
            "message": "Message sent successfully",
            "room_id": request.room_id,
            "timestamp": metadata["timestamp"],
            "did": metadata["did"]
        }
    except ValidationError as e:
        logger.error(f"Validation error sending Matrix message: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending Matrix message: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error sending message: {str(e)}")
