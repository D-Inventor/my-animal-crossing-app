from dataclasses import dataclass

from sqlalchemy.orm import Session

from .domain import Amiibo

# BUSINESS RULES
# Given an Amiibo id:
# Fetch the amiibo from the database by the "head" of the id
# If found, return the amiibo's id and name
# If not found, return an AmiiboNotFoundError


@dataclass(frozen=True)
class GetAmiiboByIDQuery:
    id: str


def handle_get_amiibo_by_id(
    session: Session,
    query: GetAmiiboByIDQuery,
) -> GetAmiiboByIDResult | AmiiboNotFoundError:
    # Placeholder implementation
    amiibo = session.get(Amiibo, query.id)
    return (
        GetAmiiboByIDResult(id=amiibo.id, name=amiibo.name)
        if amiibo
        else AmiiboNotFoundError()
    )


@dataclass(frozen=True)
class GetAmiiboByIDResult:
    id: str
    name: str


@dataclass(frozen=True)
class AmiiboNotFoundError:
    pass
