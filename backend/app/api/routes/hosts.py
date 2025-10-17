import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import hosts
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Host,
    HostCreate,
    HostPublic,
    HostsPublic,
    HostUpdate,
)

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=HostsPublic,
)
def read_hosts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve hosts.
    """

    count_statement = select(func.count()).select_from(Host)
    count = session.exec(count_statement).one()

    statement = select(Host).offset(skip).limit(limit)
    hosts = session.exec(statement).all()

    return HostsPublic(data=hosts, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=HostPublic,
)
def create_host(*, session: SessionDep, host_in: HostCreate) -> Any:
    """
    Create new host.
    """
    host = hosts.get_host_by_name(session=session, name=host_in.name)
    if host:
        raise HTTPException(
            status_code=400,
            detail="The host with this host name already exists in the system.",
        )

    host = hosts.create_host(session=session, host_create=host_in)
    return host


@router.get("/{id}", response_model=HostPublic)
def read_host_by_id(
    id: uuid.UUID, session: SessionDep, current_host: CurrentUser
) -> Any:
    """
    Get a specific host by id.
    """
    host = session.get(Host, id)

    if not current_host.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The host doesn't have enough privileges",
        )
    return host


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=HostPublic,
)
def update_host(
    *,
    session: SessionDep,
    id: uuid.UUID,
    host_in: HostUpdate,
) -> Any:
    """
    Update a host.
    """

    db_host = session.get(Host, id)
    if not db_host:
        raise HTTPException(
            status_code=404,
            detail="The host with this id does not exist in the system",
        )
    db_host = hosts.update_host(session=session, db_host=db_host, host_in=host_in)
    return db_host


@router.delete("/{id}")
def delete_host(
    session: SessionDep, current_host: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    host = session.get(Host, id)
    if not host:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_host.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(host)
    session.commit()
    return Message(message="Host deleted successfully")
