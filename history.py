import json
from config import HISTORY_FILE


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"posted": []}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def is_posted(identifier):
    return identifier in load_history()["posted"]


def mark_posted(identifier):
    history = load_history()
    history["posted"].append(identifier)
    save_history(history)


def all_parts_posted(video_stem, total_parts):
    history = load_history()
    for part in range(1, total_parts + 1):
        if f"{video_stem}_part{part}" not in history["posted"]:
            return False
    return True
