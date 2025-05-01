from nio import AsyncClient, MatrixRoom, RoomMessageText
import json
from datetime import datetime
import hashlib
import os

# Hardcoded Matrix homeserver and room ID for temporary use
HOMESERVER = "https://matrix.org"
ROOM_ID = "!mockedroomid:matrix.org"
ACCESS_TOKEN = "mocked-access-token-for-development"

async def send_audit_root(run_ids, results_dir="./results"):
    """Send an audit root message to the transparency room with SHA256 digest of results."""
    client = AsyncClient(HOMESERVER, "@bot:matrix.org")
    client.access_token = ACCESS_TOKEN
    
    try:
        # Login to Matrix
        await client.login(ACCESS_TOKEN)
        
        # Calculate SHA256 digest of all JSON files in results directory
        digest = calculate_results_digest(results_dir)
        
        # Format audit message
        audit_message = {
            "type": "audit-root",
            "sha256": digest,
            "timestamp": datetime.utcnow().isoformat(),
            "run_ids": run_ids
        }
        
        # Send message to the room
        await client.room_send(
            room_id=ROOM_ID,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": json.dumps(audit_message, indent=2)
            }
        )
        
        print(f"Audit root sent to {ROOM_ID}: {digest}")
        return audit_message
        
    finally:
        await client.close()

def calculate_results_digest(results_dir):
    """Calculate SHA256 digest of all JSON files in the results directory."""
    if not os.path.exists(results_dir):
        return "no-results-directory"
    
    hasher = hashlib.sha256()
    for filename in sorted(os.listdir(results_dir)):
        if filename.endswith(".json"):
            file_path = os.path.join(results_dir, filename)
            with open(file_path, "rb") as f:
                content = f.read()
                hasher.update(content)
    
    return hasher.hexdigest()
