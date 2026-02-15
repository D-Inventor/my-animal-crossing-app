import time
from typing import Iterator

from features.example_feature import get_example_payload


def fake_event_stream(count: int = 3) -> Iterator[dict]:
    for i in range(count):
        yield {"event_id": i, "signal": "match_request"}


def perform_automatch(event: dict) -> dict:
    # Example automatch behaviour that uses the shared feature
    payload = get_example_payload()
    return {"event": event, "result": "matched", "feature": payload}


def run() -> None:
    print("[automatcher] starting example automatcher")
    for ev in fake_event_stream():
        print(f"[automatcher] got event: {ev}")
        out = perform_automatch(ev)
        print(f"[automatcher] match result: {out}")
        time.sleep(0.5)


if __name__ == "__main__":
    run()
