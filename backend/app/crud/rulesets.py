from typing import Any

from sqlmodel import Session, select
from app.models import Ruleset, RulesetCreate, RulesetUpdate


def get_ruleset_by_name(*, session: Session, name: str) -> Ruleset | None:
    statement = select(Ruleset).where(Ruleset.name == name)
    session_ruleset = session.exec(statement).first()
    return session_ruleset


def create_ruleset(*, session: Session, ruleset_create: RulesetCreate) -> Ruleset:
    db_obj = Ruleset.model_validate(ruleset_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_ruleset(
    *, session: Session, db_ruleset: Ruleset, ruleset_in: RulesetUpdate
) -> Any:
    ruleset_data = ruleset_in.model_dump(exclude_unset=True)
    extra_data = {}
    db_ruleset.sqlmodel_update(ruleset_data, update=extra_data)
    session.add(db_ruleset)
    session.commit()
    session.refresh(db_ruleset)
    return db_ruleset
