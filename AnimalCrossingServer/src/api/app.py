from fastapi import FastAPI

from api.db.config import configure_database
from api.villagers import router as villagers_router

app = FastAPI(title="Animal Crossing API")
app.include_router(villagers_router)

configure_database(app)
