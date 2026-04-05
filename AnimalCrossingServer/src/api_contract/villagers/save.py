from pydantic import BaseModel


class SaveVillagerRequest(BaseModel):
    name: str
