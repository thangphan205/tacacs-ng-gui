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
def create_rulesetscriptset(
    *, session: SessionDep, rulesetscriptset_in: RulesetScriptSetCreate
) -> Any:
    """
    Create new rulesetscriptset.
    """

    rulesetscriptset = rulesetscriptsets.create_rulesetscriptset(
        session=session, rulesetscriptset_create=rulesetscriptset_in
    )
    return rulesetscriptset


@router.get("/{id}", response_model=RulesetScriptSetPublic)
def read_rulesetscriptset_by_id(
    id: uuid.UUID, session: SessionDep, current_rulesetscriptset: CurrentUser
) -> Any:
    """
    Get a specific rulesetscriptset by id.
    """
    rulesetscriptset = session.get(RulesetScriptSet, id)

    if not current_rulesetscriptset.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The rulesetscriptset doesn't have enough privileges",
        )
    return rulesetscriptset


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptSetPublic,
)
def update_rulesetscriptset(
    *,
    session: SessionDep,
    id: uuid.UUID,
    rulesetscriptset_in: RulesetScriptSetUpdate,
) -> Any:
    """
    Update a rulesetscriptset.
    """

    db_rulesetscriptset = session.get(RulesetScriptSet, id)
    if not db_rulesetscriptset:
        raise HTTPException(
            status_code=404,
            detail="The rulesetscriptset with this id does not exist in the system",
        )
    db_rulesetscriptset = rulesetscriptsets.update_rulesetscriptset(
        session=session,
        db_rulesetscriptset=db_rulesetscriptset,
        rulesetscriptset_in=rulesetscriptset_in,
    )
    return db_rulesetscriptset


@router.delete("/{id}")
def delete_rulesetscriptset(
    session: SessionDep, current_rulesetscriptset: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    rulesetscriptset = session.get(RulesetScriptSet, id)
    if not rulesetscriptset:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_rulesetscriptset.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(rulesetscriptset)
    session.commit()
    return Message(message="RulesetScriptSet deleted successfully")
