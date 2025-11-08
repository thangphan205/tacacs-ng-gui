import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.crud import tacacs_configs
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    TacacsConfig,
    TacacsConfigCreate,
    TacacsConfigPublic,
    TacacsConfigsPublic,
    TacacsConfigUpdate,
)

router = APIRouter(prefix="/tacacs_configs", tags=["tacacs_configs"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsConfigsPublic,
)
def read_tacacs_configs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Any:
    """
    Retrieve tacacs_configs.
    """

    count_statement = select(func.count()).select_from(TacacsConfig)
    count = session.exec(count_statement).one()
    sort_column = getattr(TacacsConfig, sort_by, None)
    if sort_column is None:
        raise HTTPException(status_code=400, detail=f"Invalid sort column: {sort_by}")
    order = sort_column.desc() if sort_order == "desc" else sort_column.asc()
    statement = select(TacacsConfig).order_by(order).offset(skip).limit(limit)
    tacacs_configs = session.exec(statement).all()

    return TacacsConfigsPublic(data=tacacs_configs, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsConfigPublic,
)
def create_tacacs_config(
    *, session: SessionDep, tacacs_config_in: TacacsConfigCreate
) -> Any:
    """
    Create new tacacs_config.
    """
    tacacs_config = tacacs_configs.get_tacacs_config_by_name(
        session=session, name=tacacs_config_in.filename
    )
    if tacacs_config:
        raise HTTPException(
            status_code=400,
            detail="The tacacs_config with this tacacs_config name already exists in the system.",
        )

    tacacs_config = tacacs_configs.create_tacacs_config(
        session=session, tacacs_config_create=tacacs_config_in
    )
    return tacacs_config


@router.get("/{id}", response_model=TacacsConfigPublic)
def read_tacacs_config_by_id(
    id: uuid.UUID, session: SessionDep, current_tacacs_config: CurrentUser
) -> Any:
    """
    Get a specific tacacs_config by id.
    """
    tacacs_config = session.get(TacacsConfig, id)

    if not current_tacacs_config.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The tacacs_config doesn't have enough privileges",
        )
    if not tacacs_config:
        raise HTTPException(
            status_code=404,
            detail="The tacacs_config with this id does not exist in the system",
        )
    file_content = tacacs_configs.get_tacacs_config_by_filename(tacacs_config.filename)
    tacacs_config_return = TacacsConfigPublic.model_validate(tacacs_config)
    tacacs_config_return.data = file_content
    return tacacs_config_return


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TacacsConfigPublic,
)
def update_tacacs_config(
    *,
    session: SessionDep,
    id: uuid.UUID,
    tacacs_config_in: TacacsConfigUpdate,
) -> Any:
    """
    Update a tacacs_config.
    """

    db_tacacs_config = session.get(TacacsConfig, id)
    if not db_tacacs_config:
        raise HTTPException(
            status_code=404,
            detail="The tacacs_config with this id does not exist in the system",
        )
    db_tacacs_config = tacacs_configs.update_tacacs_config(
        session=session,
        db_tacacs_config=db_tacacs_config,
        tacacs_config_in=tacacs_config_in,
    )
    return db_tacacs_config


@router.delete("/{id}")
def delete_tacacs_config(
    session: SessionDep, current_tacacs_config: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    db_tacacs_config = session.get(TacacsConfig, id)
    if not db_tacacs_config:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_tacacs_config.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    tacacs_configs.delete_tacacs_config(
        session=session, db_tacacs_config=db_tacacs_config
    )
    return Message(message="TacacsConfig deleted successfully")
