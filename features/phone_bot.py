# ============================================================
#  FEATURE: CHAT WITH THE APP FROM YOUR PHONE
#  Free Telegram bot. It starts itself in the background when
#  TELEGRAM_BOT_TOKEN is set in config.py. Messages you send
#  from your phone go through the SAME brain as the desktop app.
# ============================================================

import threading
import time

import requests

import config
from core.feature import Feature
from notifications import telegram as tg


class PhoneBot(Feature):
    name = "phone chat"
    button = "Phone Chat Setup"
    priority = 95
    _started = False

    def can_handle(self, text):
        return "phone chat" in text or "telegram" in text

    def on_button(self, app):
        if not config.TELEGRAM_BOT_TOKEN.strip():
            return ("Phone chat isn't switched on yet. It's free:\n"
                    "1. Open Telegram and message @BotFather\n"
                    "2. Send /newbot, pick any name and username\n"
                    "3. Copy the token it gives you into config.py:\n"
                    "   TELEGRAM_BOT_TOKEN = \"paste token here\"\n"
                    "4. Restart the app, message your bot 'hi' once,\n"
                    "   then ask it 'how are my stocks going?' from your phone.")
        return ("Phone chat is ON. Find your bot in Telegram and try:\n"
                "  how are my stocks going?\n"
                "  should I buy reliance?\n"
                "  news\n"
                "  what is a dividend?")

    def handle(self, text, app):
        return self.on_button(app)

    def tick(self, app):
        if not config.TELEGRAM_BOT_TOKEN.strip() or self._started:
            return
        self._started = True
        threading.Thread(target=self._loop, args=(app,), daemon=True).start()

    def _loop(self, app):
        token = config.TELEGRAM_BOT_TOKEN.strip()
        base = f"https://api.telegram.org/bot{token}"
        offset = 0
        while True:
            try:
                r = requests.get(base + "/getUpdates",
                                 params={"timeout": 20, "offset": offset},
                                 timeout=30)
                for update in r.json().get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat = msg.get("chat", {}).get("id")
                    text = msg.get("text", "").strip()
                    if not chat or not text:
                        continue
                    tg.save_chat_id(chat)   # remember phone for alerts & SOS
                    answer = app.handle(text)
                    requests.post(base + "/sendMessage",
                                  data={"chat_id": chat, "text": answer[:3500]},
                                  timeout=20)
            except Exception:
                pass  # internet hiccup? just try again
            time.sleep(1)
