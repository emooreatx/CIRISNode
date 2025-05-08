from pydantic import BaseModel

class MatrixMessageRequest(BaseModel):
    room_id: str
    token: str
    message: str
