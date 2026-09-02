from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, UserResponse
from app.security import hash_password
from app.models.user import User
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    repository = UserRepository(db)

    existing_user = repository.get_by_email(data.email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже существует"
        )

    existing_user = repository.get_by_username(data.username)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким username уже существует"
        )

    password_hash = hash_password(data.password)

    user = User(
        username=data.username,
        email=data.email,
        password_hash=password_hash
    )
    created_user = repository.create(user)

    return {
        "id": created_user.id,
        "username": created_user.username,
        "email": created_user.email,
        "created_at": created_user.created_at
    }