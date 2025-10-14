import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app.crud import tacacs_groups
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    TacacsGroupUser,
    TacacsGroupUserCreate,
    TacacsGroupUserPublic,
    TacacsGroupUsersPublic,
    TacacsGroupUserUpdate,
)

router = APIRouter(prefix="/tacacs_groups", tags=["tacacs_groups"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsGroupUsersPublic,
)
def read_groups(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve groups.
    """

    count_statement = select(func.count()).select_from(TacacsGroupUser)
    count = session.exec(count_statement).one()

    statement = select(TacacsGroupUser).offset(skip).limit(limit)
    groups = session.exec(statement).all()

    return TacacsGroupUsersPublic(data=groups, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsGroupUserPublic,
)
def create_group(*, session: SessionDep, group_in: TacacsGroupUserCreate) -> Any:
    """
    Create new group.
    """
    group = tacacs_groups.get_group_by_group_name(
        session=session, group_name=group_in.group_name
    )
    if group:
        raise HTTPException(
            status_code=400,
            detail="The user with this group name already exists in the system.",
        )

    user = tacacs_groups.create_group(session=session, user_create=group_in)
    return user


@router.get("/{id}", response_model=TacacsGroupUserPublic)
def read_group_by_id(
    id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    group = session.get(TacacsGroupUser, id)

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return group


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsGroupUserPublic,
)
def update_group(
    *,
    session: SessionDep,
    id: uuid.UUID,
    group_in: TacacsGroupUserUpdate,
) -> Any:
    """
    Update a group.
    """

    db_group = session.get(TacacsGroupUser, id)
    if not db_group:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if group_in.group_name:
        existing_user = tacacs_groups.get_group_by_group_name(
            session=session, group_name=group_in.group_name
        )
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_group = tacacs_groups.update_group(
        session=session, db_group=db_group, group_in=group_in
    )
    return db_group


@router.delete("/{id}")
def delete_tacacs_group(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    tacacs_group = session.get(TacacsGroupUser, id)
    if not tacacs_group:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(tacacs_group)
    session.commit()
    return Message(message="Group deleted successfully")
