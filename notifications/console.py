# ============================================================
#  LAPTOP ALERTS (always on)
#  - Prints the alert
#  - Saves it to alerts_log.txt so you can read it after school
#  - Plays a loud Windows sound
# ============================================================

import datetime
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alerts_log.txt")


class ConsoleNotifier:
    def send(self, title, message):
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"[{stamp}] {title} | {message}"
        print("\n*** ALERT *** " + line)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONHAND)  # loud "warning" sound
        except Exception:
            pass
