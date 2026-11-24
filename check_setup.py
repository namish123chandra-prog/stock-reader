# ============================================================
#  SETUP CHECKER - run: python check_setup.py
#  Tells you if the app is ready to run cleanly.
# ============================================================

import importlib.util
import os
import sys

from config import VERSION

ok = True


def check(label, condition, hint=""):
    global ok
    print(("  OK   " if condition else "  FAIL ") + label
          + ("" if condition else "  -> " + hint))
    if not condition:
        ok = False


print(f"Stock Buddy v{VERSION} - setup check\n")
check("Python 3.9 or newer", sys.version_info >= (3, 9), sys.version)
for lib in ("yfinance", "pandas", "requests"):
    check(f"{lib} installed", importlib.util.find_spec(lib) is not None,
          "run: python -m pip install -r requirements.txt")
for folder in ("core", "features", "notifications", "ui"):
    check(f"{folder}/ folder", os.path.isdir(folder))
for file in ("run.py", "config.py", "README.md", "LICENSE"):
    check(file, os.path.isfile(file))
check("always-on launcher installed",
      os.path.exists(os.path.join(os.environ.get("APPDATA", ""), "Microsoft",
                                  "Windows", "Start Menu", "Programs",
                                  "Startup", "Stock Buddy Monitor.vbs")))

print("\nEverything looks good!" if ok else
      "\nSome things need fixing before publishing.")
