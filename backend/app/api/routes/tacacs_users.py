import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import tacacs_users
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    TacacsUser,
    TacacsUserCreate,
    TacacsUserPublic,
    TacacsUsersPublic,
    TacacsUserUpdate,
)

router = APIRouter(prefix="/tacacs_users", tags=["tacacs_users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsUsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(TacacsUser)
    count = session.exec(count_statement).one()

    statement = select(TacacsUser).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return TacacsUsersPublic(data=users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsUserPublic,
)
def create_user(*, session: SessionDep, user_in: TacacsUserCreate) -> Any:
    """
    Create new user.
    """
    user = tacacs_users.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = tacacs_users.create_user(session=session, user_create=user_in)
    return user


@router.get("/{id}", response_model=TacacsUserPublic)
def read_user_by_id(
    id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(TacacsUser, id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsUserPublic,
)
def update_user(
    *,
    session: SessionDep,
    id: uuid.UUID,
    user_in: TacacsUserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(TacacsUser, id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.username:
        existing_user = tacacs_users.get_user_by_username(
            session=session, username=user_in.username
        )
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = tacacs_users.update_user(
        session=session, db_user=db_user, user_in=user_in
    )
    return db_user


@router.delete("/{id}")
def delete_tacacs_user(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    tacacs_user = session.get(TacacsUser, id)
    if not tacacs_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(tacacs_user)
    session.commit()
    return Message(message="Item deleted successfully")
