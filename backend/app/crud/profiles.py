from typing import Any

from sqlmodel import Session, select
from app.models import Profile, ProfileCreate, ProfileUpdate


def get_profile_by_name(*, session: Session, name: str) -> Profile | None:
    statement = select(Profile).where(Profile.name == name)
    session_profile = session.exec(statement).first()
    return session_profile


def create_profile(*, session: Session, profile_create: ProfileCreate) -> Profile:
    db_obj = Profile.model_validate(profile_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_profile(
    *, session: Session, db_profile: Profile, profile_in: ProfileUpdate
) -> Any:
    profile_data = profile_in.model_dump(exclude_unset=True)
    extra_data = {}
    db_profile.sqlmodel_update(profile_data, update=extra_data)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile
