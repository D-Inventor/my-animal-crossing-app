from typing import Dict

from fastapi import FastAPI

from features.example_feature import get_example_payload

app = FastAPI(title="AnimalCrossing Example API")


@app.get("/feature")
async def feature() -> Dict[str, str]:
    """Return the example feature payload."""
    return get_example_payload()
