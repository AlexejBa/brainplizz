from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.jwt import decode_access_token
from uuid import UUID

security = HTTPBearer()

def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials

def get_current_user_id(
    token: str = Depends(get_token)) -> UUID:
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Недействительный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UUID(user_id)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()