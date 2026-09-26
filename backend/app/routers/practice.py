from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession, PracticeOwner
from app.core.responses import error_responses
from app.models.practice import Practice
from app.schemas.practice import PracticeRead, PracticeUpdate

router = APIRouter(prefix="/practice", tags=["Practice"])


def _practice_for(db, user) -> Practice:
    practice = db.get(Practice, user.practice_id)
    if practice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice not found")
    return practice


@router.get(
    "",
    response_model=PracticeRead,
    responses=error_responses(401, 404),
    summary="Get the current practice",
)
def get_practice(current_user: CurrentUser, db: DbSession) -> Practice:
    return _practice_for(db, current_user)


@router.patch(
    "",
    response_model=PracticeRead,
    responses=error_responses(401, 403, 404, 422),
    summary="Update practice settings",
)
def update_practice(payload: PracticeUpdate, owner: PracticeOwner, db: DbSession) -> Practice:
    practice = _practice_for(db, owner)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(practice, key, value)
    db.commit()
    db.refresh(practice)
    return practice
