from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user_id, get_db
from app.jwt import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security import hash_password, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
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


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    repository = UserRepository(db)

    user = repository.get_by_email(data.email)

    if not user or not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }