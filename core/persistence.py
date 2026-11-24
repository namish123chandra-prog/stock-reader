# ============================================================
#  TINY JSON FILE HELPER
#  Features use this to remember things between app restarts.
#  Files are saved next to run.py so you can find/edit them.
# ============================================================

import json
import os

BASE = os.path.dirname(os.path.dirname(__file__))


def path(filename):
    return os.path.join(BASE, filename)


def read_json(filename, default):
    try:
        with open(path(filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(filename, data):
    with open(path(filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
