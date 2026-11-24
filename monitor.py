# ============================================================
#  ALWAYS-ON MONITOR (no window)
#  The "Turn On Always-On.bat" file tells Windows to start this
#  quietly whenever you log in. It checks prices, watches your
#  stocks, sends alerts and the daily review - no app open needed.
#  To stop it: run "Turn Off Always-On.bat", or end the
#  "pythonw.exe" task in Task Manager.
# ============================================================

import logging
import os
import time

from core.app import App


def main():
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "app.log"),
        level=logging.INFO, encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Stock Buddy monitor started")

    app = App()
    app.start_background()
    print("Stock Buddy monitor is running. Alerts are active.", flush=True)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    main()
