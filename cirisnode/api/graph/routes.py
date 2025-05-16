from fastapi import APIRouter, Request, HTTPException, status, Depends
import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from cirisnode.utils.metadata import get_user_metadata

# Setup logging
logger = logging.getLogger(__name__)

graph_router = APIRouter(tags=["graph"])

@graph_router.post("/apply")
async def apply_to_graph(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        graph_type = data.get("graph_type", "ENV_GRAPH")  # Default to ENV_GRAPH if not specified
        if graph_type not in ["ENV_GRAPH", "ID_GRAPH", "JOB_GRAPH"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid graph type. Must be 'ENV_GRAPH', 'ID_GRAPH', or 'JOB_GRAPH'.")
        
        intent = data.get("intent", "update")
        update_id = str(uuid.uuid4())
        logger.info(f"Graph update applied to {graph_type} by DID: {metadata['did']}, Intent: {intent}, Update ID: {update_id}")
        logger.info(f"Graph updated: {graph_type}")
        return {
            "status": "success",
            "update_id": update_id,
            "graph_type": graph_type,
            "intent": intent,
            "message": f"Update applied to {graph_type} with intent {intent}",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error applying update to graph: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error applying update to graph: {str(e)}")

@graph_router.post("/job/assign")
async def assign_job(request: Request, metadata: Dict[str, Any] = Depends(get_user_metadata)):
    try:
        data = await request.json()
        job_id = data.get("job_id", "mock_job_id")
        target_did = data.get("target_did", "did:mock:target")
        intent = data.get("intent", "assign")
        assignment_id = str(uuid.uuid4())
        logger.info(f"Job assignment to {target_did} for Job ID: {job_id} by DID: {metadata['did']}, Intent: {intent}, Assignment ID: {assignment_id}")
        logger.info("Graph updated: JOB_GRAPH")
        return {
            "status": "success",
            "assignment_id": assignment_id,
            "job_id": job_id,
            "target_did": target_did,
            "intent": intent,
            "message": f"Job {job_id} assigned to {target_did} in JOB_GRAPH",
            "did": metadata["did"],
            "timestamp": metadata["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error assigning job: {str(e)}, DID: {metadata['did']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error assigning job: {str(e)}")
