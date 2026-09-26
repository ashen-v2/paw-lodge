from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import token_user_id
from app.models.user import ROLE_OWNER, User

bearer_scheme = HTTPBearer(auto_error=False)

UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers=UNAUTHORIZED_HEADERS,
        )
    try:
        user_id = token_user_id(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers=UNAUTHORIZED_HEADERS,
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers=UNAUTHORIZED_HEADERS,
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers=UNAUTHORIZED_HEADERS,
        )
    return user


def require_practice_owner(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != ROLE_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the practice owner can update practice settings",
        )
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
PracticeOwner = Annotated[User, Depends(require_practice_owner)]
DbSession = Annotated[Session, Depends(get_db)]
