from datetime import datetime

from features.example_feature import get_example_message


def run() -> None:
    """Simple import worker entrypoint (example).

    In a real project this would schedule or poll work. For the example it
    prints a message that includes the features example output and exits.
    """
    ts = datetime.utcnow().isoformat() + "Z"
    print(f"[import_worker] run at {ts}")
    print(f"[import_worker] feature -> {get_example_message()}")


if __name__ == "__main__":
    run()
