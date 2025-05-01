import os
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "fallback")
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
MATRIX_ROOM_ID = os.getenv("MATRIX_ROOM_ID", "!mockedroomid:matrix.org")
