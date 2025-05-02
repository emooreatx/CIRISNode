import os
from matrix_client.client import MatrixClient

def send_matrix_message(message: str):
    if os.getenv("MATRIX_LOGGING_ENABLED", "false").lower() != "true":
        return
    
    try:
        homeserver_url = os.getenv("MATRIX_HOMESERVER_URL")
        access_token = os.getenv("MATRIX_ACCESS_TOKEN")
        room_id = os.getenv("MATRIX_ROOM_ID")
        
        if not all([homeserver_url, access_token, room_id]):
            print("Matrix configuration incomplete. Skipping message send.")
            return
            
        client = MatrixClient(homeserver_url)
        client.login_with_token(access_token)
        client.room_send(room_id, "m.room.message", {"msgtype": "m.text", "body": message})
        print(f"Matrix message sent: {message}")
    except Exception as e:
        print(f"Failed to send Matrix message: {e}")
