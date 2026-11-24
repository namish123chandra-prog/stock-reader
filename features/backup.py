# ============================================================
#  FEATURE: BACKUP BUTTON
#  Saves a dated ZIP of the whole app (code + your saved stocks)
#  into the "backups" folder. Great before updating or publishing.
# ============================================================

import datetime
import os
import zipfile

from core.feature import Feature
from core.persistence import BASE

SKIP_DIRS = {"backups", "__pycache__", ".git", ".pytest_cache"}


def create_backup():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(BASE, "backups")
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, f"StockBuddy_backup_{stamp}.zip")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(BASE):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name.endswith((".pyc", ".zip")):
                    continue
                full = os.path.join(root, name)
                arc = os.path.relpath(full, BASE)
                try:
                    z.write(full, arc)
                except Exception:
                    pass
    return dest


class Backup(Feature):
    name = "backup"
    button = "Backup"
    priority = 30   # single word, answer before stock checker treats it as a ticker

    def can_handle(self, text):
        return ("backup" in text or "save a copy" in text)

    def handle(self, text, app):
        dest = create_backup()
        size = os.path.getsize(dest) / 1024
        return (f"Backup done! ✅\n{dest}\n"
                f"Size: {size:.0f} KB. Copy this ZIP somewhere safe "
                "(Google Drive, pen drive) before sharing or updating the app.")
