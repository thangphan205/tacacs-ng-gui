import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import services
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Service,
    ServiceCreate,
    ServicePublic,
    ServicesPublic,
    ServiceUpdate,
)

router = APIRouter(prefix="/services", tags=["services"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ServicesPublic,
)
def read_services(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve services.
    """

    count_statement = select(func.count()).select_from(Service)
    count = session.exec(count_statement).one()

    statement = select(Service).offset(skip).limit(limit)
    services = session.exec(statement).all()

    return ServicesPublic(data=services, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ServicePublic,
)
def create_service(*, session: SessionDep, service_in: ServiceCreate) -> Any:
    """
    Create new service.
    """
    service = services.get_service_by_name(session=session, name=service_in.name)
    if service:
        raise HTTPException(
            status_code=400,
            detail="The service with this service name already exists in the system.",
        )

    service = services.create_service(session=session, service_create=service_in)
    return service


@router.get("/{id}", response_model=ServicePublic)
def read_service_by_id(
    id: uuid.UUID, session: SessionDep, current_service: CurrentUser
) -> Any:
    """
    Get a specific service by id.
    """
    service = session.get(Service, id)

    if not current_service.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The service doesn't have enough privileges",
        )
    return service


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ServicePublic,
)
def update_service(
    *,
    session: SessionDep,
    id: uuid.UUID,
    service_in: ServiceUpdate,
) -> Any:
    """
    Update a service.
    """

    db_service = session.get(Service, id)
    if not db_service:
        raise HTTPException(
            status_code=404,
            detail="The service with this id does not exist in the system",
        )
    db_service = services.update_service(
        session=session, db_service=db_service, service_in=service_in
    )
    return db_service


@router.delete("/{id}")
def delete_service(
    session: SessionDep, current_service: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    service = session.get(Service, id)
    if not service:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_service.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(service)
    session.commit()
    return Message(message="Service deleted successfully")
