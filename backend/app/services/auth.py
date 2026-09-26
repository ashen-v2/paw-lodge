from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.practice import Practice
from app.models.user import ROLE_OWNER, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def register_practice(db: Session, payload: RegisterRequest) -> User:
    existing = db.scalar(select(User.id).where(func.lower(User.email) == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    practice = Practice(name=payload.practice_name)
    db.add(practice)
    db.flush()
    user = User(
        practice_id=practice.id,
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=ROLE_OWNER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    token = create_access_token(user_id=user.id, practice_id=user.practice_id, role=user.role)
    return TokenResponse(access_token=token)
