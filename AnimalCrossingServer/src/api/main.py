from fastapi import FastAPI

from .features.amiibo import router as amiibo
from .features.characters import router as characters

app = FastAPI()

app.include_router(amiibo.router)
app.include_router(characters.router)
