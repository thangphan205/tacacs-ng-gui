import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import profiles
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Profile,
    ProfileCreate,
    ProfilePublic,
    ProfilesPublic,
    ProfileUpdate,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilesPublic,
)
def read_profiles(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve profiles.
    """

    count_statement = select(func.count()).select_from(Profile)
    count = session.exec(count_statement).one()

    statement = select(Profile).offset(skip).limit(limit)
    profiles = session.exec(statement).all()

    return ProfilesPublic(data=profiles, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilePublic,
)
def create_profile(*, session: SessionDep, profile_in: ProfileCreate) -> Any:
    """
    Create new profile.
    """
    profile = profiles.get_profile_by_name(session=session, name=profile_in.name)
    if profile:
        raise HTTPException(
            status_code=400,
            detail="The profile with this profile name already exists in the system.",
        )

    profile = profiles.create_profile(session=session, profile_create=profile_in)
    return profile


@router.get("/{id}", response_model=ProfilePublic)
def read_profile_by_id(
    id: uuid.UUID, session: SessionDep, current_profile: CurrentUser
) -> Any:
    """
    Get a specific profile by id.
    """
    profile = session.get(Profile, id)

    if not current_profile.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The profile doesn't have enough privileges",
        )
    return profile


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProfilePublic,
)
def update_profile(
    *,
    session: SessionDep,
    id: uuid.UUID,
    profile_in: ProfileUpdate,
) -> Any:
    """
    Update a profile.
    """

    db_profile = session.get(Profile, id)
    if not db_profile:
        raise HTTPException(
            status_code=404,
            detail="The profile with this id does not exist in the system",
        )
    db_profile = profiles.update_profile(
        session=session, db_profile=db_profile, profile_in=profile_in
    )
    return db_profile


@router.delete("/{id}")
def delete_profile(
    session: SessionDep, current_profile: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    profile = session.get(Profile, id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_profile.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(profile)
    session.commit()
    return Message(message="Profile deleted successfully")
