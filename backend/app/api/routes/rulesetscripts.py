import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import rulesetscripts
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    RulesetScript,
    RulesetScriptCreate,
    RulesetScriptPublic,
    RulesetScriptsPublic,
    RulesetScriptUpdate,
)

router = APIRouter(prefix="/rulesetscripts", tags=["rulesetscripts"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptsPublic,
)
def read_rulesetscripts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve rulesetscripts.
    """

    count_statement = select(func.count()).select_from(RulesetScript)
    count = session.exec(count_statement).one()

    statement = select(RulesetScript).offset(skip).limit(limit)
    rulesetscripts = session.exec(statement).all()

    return RulesetScriptsPublic(data=rulesetscripts, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptPublic,
)
def create_rulesetscript(
    *, session: SessionDep, rulesetscript_in: RulesetScriptCreate
) -> Any:
    """
    Create new rulesetscript.
    """
    # rulesetscript = rulesetscripts.get_rulesetscript_by_name(
    #     session=session, name=rulesetscript_in.name
    # )
    # if rulesetscript:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="The rulesetscript with this rulesetscript name already exists in the system.",
    #     )

    rulesetscript = rulesetscripts.create_rulesetscript(
        session=session, rulesetscript_create=rulesetscript_in
    )
    return rulesetscript


@router.get("/{id}", response_model=RulesetScriptPublic)
def read_rulesetscript_by_id(
    id: uuid.UUID, session: SessionDep, current_rulesetscript: CurrentUser
) -> Any:
    """
    Get a specific rulesetscript by id.
    """
    rulesetscript = session.get(RulesetScript, id)

    if not current_rulesetscript.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The rulesetscript doesn't have enough privileges",
        )
    return rulesetscript


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RulesetScriptPublic,
)
def update_rulesetscript(
    *,
    session: SessionDep,
    id: uuid.UUID,
    rulesetscript_in: RulesetScriptUpdate,
) -> Any:
    """
    Update a rulesetscript.
    """

    db_rulesetscript = session.get(RulesetScript, id)
    if not db_rulesetscript:
        raise HTTPException(
            status_code=404,
            detail="The rulesetscript with this id does not exist in the system",
        )
    db_rulesetscript = rulesetscripts.update_rulesetscript(
        session=session,
        db_rulesetscript=db_rulesetscript,
        rulesetscript_in=rulesetscript_in,
    )
    return db_rulesetscript


@router.delete("/{id}")
def delete_rulesetscript(
    session: SessionDep, current_rulesetscript: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    rulesetscript = session.get(RulesetScript, id)
    if not rulesetscript:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_rulesetscript.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(rulesetscript)
    session.commit()
    return Message(message="RulesetScript deleted successfully")
