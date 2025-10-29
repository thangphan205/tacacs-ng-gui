import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import rulesetscriptsets
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    RulesetScriptSet,
    RulesetScriptSetCreate,
    RulesetScriptSetPublic,
    RulesetScriptSetsPublic,
    RulesetScriptSetUpdate,
)

router = APIRouter(prefix="/rulesetscriptsets", tags=["rulesetscriptsets"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptSetsPublic,
)
def read_rulesetscriptsets(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve rulesetscriptsets.
    """

    count_statement = select(func.count()).select_from(RulesetScriptSet)
    count = session.exec(count_statement).one()

    statement = select(RulesetScriptSet).offset(skip).limit(limit)
    rulesetscriptsets = session.exec(statement).all()

    return RulesetScriptSetsPublic(data=rulesetscriptsets, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptSetPublic,
)
def create_profilescriptset(
    *, session: SessionDep, profilescriptset_in: RulesetScriptSetCreate
) -> Any:
    """
    Create new profilescriptset.
    """

    profilescriptset = rulesetscriptsets.create_profilescriptset(
        session=session, profilescriptset_create=profilescriptset_in
    )
    return profilescriptset


@router.get("/{id}", response_model=RulesetScriptSetPublic)
def read_profilescriptset_by_id(
    id: uuid.UUID, session: SessionDep, current_profilescriptset: CurrentUser
) -> Any:
    """
    Get a specific profilescriptset by id.
    """
    profilescriptset = session.get(RulesetScriptSet, id)

    if not current_profilescriptset.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The profilescriptset doesn't have enough privileges",
        )
    return profilescriptset


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptSetPublic,
)
def update_profilescriptset(
    *,
    session: SessionDep,
    id: uuid.UUID,
    profilescriptset_in: RulesetScriptSetUpdate,
) -> Any:
    """
    Update a profilescriptset.
    """

    db_profilescriptset = session.get(RulesetScriptSet, id)
    if not db_profilescriptset:
        raise HTTPException(
            status_code=404,
            detail="The profilescriptset with this id does not exist in the system",
        )
    db_profilescriptset = rulesetscriptsets.update_profilescriptset(
        session=session,
        db_profilescriptset=db_profilescriptset,
        profilescriptset_in=profilescriptset_in,
    )
    return db_profilescriptset


@router.delete("/{id}")
def delete_profilescriptset(
    session: SessionDep, current_profilescriptset: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    profilescriptset = session.get(RulesetScriptSet, id)
    if not profilescriptset:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_profilescriptset.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(profilescriptset)
    session.commit()
    return Message(message="RulesetScriptSet deleted successfully")
