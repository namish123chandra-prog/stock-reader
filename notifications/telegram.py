# ============================================================
#  TELEGRAM - two-way chat from your phone (FREE!)
#  The bot replies to whatever you message it, using the very
#  same brain as the desktop app ("how are my stocks going?").
#  Setup: message @BotFather on Telegram -> /newbot -> paste
#  the token into config.py -> message your bot once.
# ============================================================

import json
import os

import requests

CHAT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "telegram_chat.json")


def save_chat_id(chat_id):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump({"chat_id": chat_id}, f)


def get_chat_id():
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("chat_id")
    except Exception:
        return None


class TelegramNotifier:
    """Used by the app to PUSH messages (Hi, SOS, alerts, review)."""

    def __init__(self, token):
        self.token = token

    def send(self, title, message):
        chat_id = get_chat_id()
        if not chat_id:
            return  # nobody has messaged the bot yet
        requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data={"chat_id": chat_id,
                  "text": f"{title}: {message}"[:3500]},
            timeout=20,
        )
