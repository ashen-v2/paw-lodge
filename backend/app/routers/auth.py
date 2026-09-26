from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.responses import error_responses
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services.auth import login, register_practice

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses=error_responses(409, 422),
    summary="Register a practice and its owner",
)
def register(payload: RegisterRequest, db: DbSession) -> UserRead:
    return register_practice(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses=error_responses(401, 422),
    summary="Log in with email and password",
)
def login_user(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return login(db, payload)


@router.get(
    "/me",
    response_model=UserRead,
    responses=error_responses(401),
    summary="Return the authenticated user",
)
def me(current_user: CurrentUser) -> UserRead:
    return current_user
