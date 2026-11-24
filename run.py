# ============================================================
#  START STOCK BUDDY
#  Double-click this file, or run:  python run.py
#  Prefer no window? Run:          python run.py --text
# ============================================================

import logging
import os
import sys


def main():
    # Make sure rupee signs / emoji don't crash the console on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    from config import VERSION

    if "--version" in sys.argv:
        print(f"Stock Buddy v{VERSION}")
        return
    if "--help" in sys.argv:
        print("Stock Buddy - simple Indian stock helper\n")
        print("  python run.py           Open the desktop window")
        print("  python run.py --text    Chat in the terminal")
        print("  python run.py --version Show the version")
        print("  python run.py --help    Show this message")
        return

    logging.basicConfig(
        filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "app.log"),
        level=logging.INFO, encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Stock Buddy started")

    from core.app import App
    app = App()
    app.start_background()

    if "--text" in sys.argv:
        print("STOCK BUDDY (text mode). Type 'help' to begin, 'quit' to exit.\n")
        while True:
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if text.lower() in ("quit", "exit", "bye"):
                break
            print("\nBuddy: " + app.handle(text) + "\n")
        app.stop()
    else:
        from ui.gui import BuddyGUI
        BuddyGUI(app).run()


if __name__ == "__main__":
    main()
