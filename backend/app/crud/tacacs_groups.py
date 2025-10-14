from typing import Any

from sqlmodel import Session, select
from app.models import TacacsGroupUser, TacacsGroupUserCreate, TacacsGroupUserUpdate


def get_group_by_group_name(
    *, session: Session, group_name: str
) -> TacacsGroupUser | None:
    statement = select(TacacsGroupUser).where(TacacsGroupUser.group_name == group_name)
    session_user = session.exec(statement).first()
    return session_user


def create_group(
    *, session: Session, user_create: TacacsGroupUserCreate
) -> TacacsGroupUser:
    db_obj = TacacsGroupUser.model_validate(user_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_group(
    *, session: Session, db_user: TacacsGroupUser, group_in: TacacsGroupUserUpdate
) -> Any:
    user_data = group_in.model_dump(exclude_unset=True)
    extra_data = {}
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
