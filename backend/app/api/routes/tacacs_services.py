import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import tacacs_services
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    TacacsService,
    TacacsServiceCreate,
    TacacsServicePublic,
    TacacsServicesPublic,
    TacacsServiceUpdate,
)

router = APIRouter(prefix="/tacacs_services", tags=["tacacs_services"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsServicesPublic,
)
def read_tacacs_services(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve tacacs_services.
    """

    count_statement = select(func.count()).select_from(TacacsService)
    count = session.exec(count_statement).one()

    statement = select(TacacsService).offset(skip).limit(limit)
    tacacs_services = session.exec(statement).all()

    return TacacsServicesPublic(data=tacacs_services, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsServicePublic,
)
def create_tacacs_service(
    *, session: SessionDep, tacacs_service_in: TacacsServiceCreate
) -> Any:
    """
    Create new tacacs_service.
    """
    tacacs_service = tacacs_services.get_tacacs_service_by_name(
        session=session, name=tacacs_service_in.name
    )
    if tacacs_service:
        raise HTTPException(
            status_code=400,
            detail="The tacacs_service with this tacacs_service name already exists in the system.",
        )

    tacacs_service = tacacs_services.create_tacacs_service(
        session=session, tacacs_service_create=tacacs_service_in
    )
    return tacacs_service


@router.get("/{id}", response_model=TacacsServicePublic)
def read_tacacs_service_by_id(
    id: uuid.UUID, session: SessionDep, current_tacacs_service: CurrentUser
) -> Any:
    """
    Get a specific tacacs_service by id.
    """
    tacacs_service = session.get(TacacsService, id)

    if not current_tacacs_service.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The tacacs_service doesn't have enough privileges",
        )
    return tacacs_service


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsServicePublic,
)
def update_tacacs_service(
    *,
    session: SessionDep,
    id: uuid.UUID,
    tacacs_service_in: TacacsServiceUpdate,
) -> Any:
    """
    Update a tacacs_service.
    """

    db_tacacs_service = session.get(TacacsService, id)
    if not db_tacacs_service:
        raise HTTPException(
            status_code=404,
            detail="The tacacs_service with this id does not exist in the system",
        )
    db_tacacs_service = tacacs_services.update_tacacs_service(
        session=session,
        db_tacacs_service=db_tacacs_service,
        tacacs_service_in=tacacs_service_in,
    )
    return db_tacacs_service


@router.delete("/{id}")
def delete_tacacs_service(
    session: SessionDep, current_tacacs_service: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    tacacs_service = session.get(TacacsService, id)
    if not tacacs_service:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_tacacs_service.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(tacacs_service)
    session.commit()
    return Message(message="TacacsService deleted successfully")
