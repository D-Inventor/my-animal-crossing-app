from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database import get_db_session
from .getbyid import (
    GetAmiiboByIDQuery,
    GetAmiiboByIDResult,
    handle_get_amiibo_by_id,
)

router = APIRouter(
    prefix="/api/amiibo",
    tags=["amiibo"],
)


class GetAmiiboByIDApiResponse(BaseModel):
    id: str
    name: str


@router.get("/{amiibo_id}", responses={404: {}})
async def get_amiibo_by_id(
    amiibo_id: str, session: Annotated[Session, Depends(get_db_session)]
) -> GetAmiiboByIDApiResponse:
    result = handle_get_amiibo_by_id(session, GetAmiiboByIDQuery(id=amiibo_id))
    if isinstance(result, GetAmiiboByIDResult):
        return GetAmiiboByIDApiResponse(id=result.id, name=result.name)
    else:
        raise HTTPException(status_code=404, detail="Amiibo not found")
