import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import profilescriptsets
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    ProfileScriptSet,
    ProfileScriptSetCreate,
    ProfileScriptSetPublic,
    ProfileScriptSetsPublic,
    ProfileScriptSetUpdate,
)

router = APIRouter(prefix="/profilescriptsets", tags=["profilescriptsets"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptSetsPublic,
)
def read_profilescriptsets(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve profilescriptsets.
    """

    count_statement = select(func.count()).select_from(ProfileScriptSet)
    count = session.exec(count_statement).one()

    statement = select(ProfileScriptSet).offset(skip).limit(limit)
    profilescriptsets = session.exec(statement).all()

    return ProfileScriptSetsPublic(data=profilescriptsets, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptSetPublic,
)
def create_profilescriptset(
    *, session: SessionDep, profilescriptset_in: ProfileScriptSetCreate
) -> Any:
    """
    Create new profilescriptset.
    """

    profilescriptset = profilescriptsets.create_profilescriptset(
        session=session, profilescriptset_create=profilescriptset_in
    )
    return profilescriptset


@router.get("/{id}", response_model=ProfileScriptSetPublic)
def read_profilescriptset_by_id(
    id: uuid.UUID, session: SessionDep, current_profilescriptset: CurrentUser
) -> Any:
    """
    Get a specific profilescriptset by id.
    """
    profilescriptset = session.get(ProfileScriptSet, id)

    if not current_profilescriptset.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The profilescriptset doesn't have enough privileges",
        )
    return profilescriptset


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfileScriptSetPublic,
)
def update_profilescriptset(
    *,
    session: SessionDep,
    id: uuid.UUID,
    profilescriptset_in: ProfileScriptSetUpdate,
) -> Any:
    """
    Update a profilescriptset.
    """

    db_profilescriptset = session.get(ProfileScriptSet, id)
    if not db_profilescriptset:
        raise HTTPException(
            status_code=404,
            detail="The profilescriptset with this id does not exist in the system",
        )
    db_profilescriptset = profilescriptsets.update_profilescriptset(
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
    profilescriptset = session.get(ProfileScriptSet, id)
    if not profilescriptset:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_profilescriptset.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(profilescriptset)
    session.commit()
    return Message(message="ProfileScriptSet deleted successfully")
