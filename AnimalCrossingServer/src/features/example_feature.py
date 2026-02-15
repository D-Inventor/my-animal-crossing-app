from typing import Dict


def get_example_message() -> str:
    """Return a short message used by example projects."""
    return "features: example feature active"


def get_example_payload() -> Dict[str, str]:
    return {"message": get_example_message()}
