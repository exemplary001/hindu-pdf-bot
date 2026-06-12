import json
from pathlib import Path

STATE_FILE = Path("data/state.json")


def get_last_successful_date():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f).get(
                "last_successful_date", ""
            )
    except Exception:
        return ""


def save_successful_date(date_str):
    with open(STATE_FILE, "w") as f:
        json.dump(
            {
                "last_successful_date": date_str
            },
            f,
            indent=4
        )