from fastapi import FastAPI

from api.villagers import router as villagers_router

app = FastAPI(title="Animal Crossing API")
app.include_router(villagers_router)
