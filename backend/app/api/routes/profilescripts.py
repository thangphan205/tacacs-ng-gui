import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import profilescripts
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    ProfileScript,
    ProfileScriptCreate,
    ProfileScriptPublic,
    ProfileScriptsPublic,
    ProfileScriptUpdate,
)

router = APIRouter(prefix="/profilescripts", tags=["profilescripts"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptsPublic,
)
def read_profilescripts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve profilescripts.
    """

    count_statement = select(func.count()).select_from(ProfileScript)
    count = session.exec(count_statement).one()

    statement = select(ProfileScript).offset(skip).limit(limit)
    profilescripts = session.exec(statement).all()

    return ProfileScriptsPublic(data=profilescripts, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptPublic,
)
def create_profilescript(
    *, session: SessionDep, profilescript_in: ProfileScriptCreate
) -> Any:
    """
    Create new profilescript.
    """
    # profilescript = profilescripts.get_profilescript_by_name(
    #     session=session, name=profilescript_in.name
    # )
    # if profilescript:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="The profilescript with this profilescript name already exists in the system.",
    #     )

    profilescript = profilescripts.create_profilescript(
        session=session, profilescript_create=profilescript_in
    )
    return profilescript


@router.get("/{id}", response_model=ProfileScriptPublic)
def read_profilescript_by_id(
    id: uuid.UUID, session: SessionDep, current_profilescript: CurrentUser
) -> Any:
    """
    Get a specific profilescript by id.
    """
    profilescript = session.get(ProfileScript, id)

    if not current_profilescript.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The profilescript doesn't have enough privileges",
        )
    return profilescript


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptPublic,
)
def update_profilescript(
    *,
    session: SessionDep,
    id: uuid.UUID,
    profilescript_in: ProfileScriptUpdate,
) -> Any:
    """
    Update a profilescript.
    """

    db_profilescript = session.get(ProfileScript, id)
    if not db_profilescript:
        raise HTTPException(
            status_code=404,
            detail="The profilescript with this id does not exist in the system",
        )
    db_profilescript = profilescripts.update_profilescript(
        session=session,
        db_profilescript=db_profilescript,
        profilescript_in=profilescript_in,
    )
    return db_profilescript


@router.delete("/{id}")
def delete_profilescript(
    session: SessionDep, current_profilescript: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    profilescript = session.get(ProfileScript, id)
    if not profilescript:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_profilescript.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(profilescript)
    session.commit()
    return Message(message="ProfileScript deleted successfully")
