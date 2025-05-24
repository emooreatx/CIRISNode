from fastapi import APIRouter, HTTPException, status, Depends, Form, Header
from cirisnode.database import get_db
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt

SECRET_KEY = "testsecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

auth_router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: str = "anonymous"


@auth_router.post("/auth/token", response_model=Token)
def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db),
):
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    row = conn.execute(
        "SELECT password, role FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if row is None:
        # Auto-create user with anonymous role
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, 'anonymous')",
            (username, password),
        )
        conn.commit()
        role = "anonymous"
    else:
        stored_pw, role = row
        if stored_pw != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    to_encode = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@auth_router.post("/auth/refresh", response_model=Token)
def refresh_access_token(Authorization: str = Header(...)):
    # Extract token from header
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = Authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role", "anonymous")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Issue new token
    to_encode = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}
