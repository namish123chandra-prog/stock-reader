# ============================================================
#  FEATURE: THEME TOGGLE
#  Switches the window between dark and light. Restart to apply.
# ============================================================

from core.feature import Feature
from core.persistence import read_json, write_json


class Theme(Feature):
    name = "theme"
    button = "Theme"
    priority = 31

    def can_handle(self, text):
        return ("theme" in text or "light mode" in text or "dark mode" in text)

    def handle(self, text, app):
        current = read_json("theme.json", {}).get("theme", "dark")
        if "light" in text:
            chosen = "light"
        elif "dark" in text:
            chosen = "dark"
        else:
            chosen = "light" if current == "dark" else "dark"
        write_json("theme.json", {"theme": chosen})
        return (f"Theme set to {chosen.upper()}. Close and reopen the app "
                "to see it. (Your choice is saved.)")
