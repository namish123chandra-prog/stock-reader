# ============================================================
#  THE ENGINE
#  - Finds every feature file in the "features" folder automatically
#  - Routes your chat messages to the right feature
#  - Runs background ticks (price watching) once a minute
#  - Sends alerts through every notification channel
#  You never need to edit this file to add a feature.
# ============================================================

import importlib
import pkgutil
import threading
import time
import traceback

import config
from core.feature import Feature
from notifications.console import ConsoleNotifier
from notifications.sms import SmsNotifier
from notifications.whatsapp import WhatsAppNotifier
from notifications.telegram import TelegramNotifier, get_chat_id


class App:
    def __init__(self):
        self.features = self._load_features()
        self.notifiers = [ConsoleNotifier()]
        if config.SMS_API_KEY.strip():
            self.notifiers.append(SmsNotifier(config.SMS_API_KEY, config.PHONE_NUMBER))
        if all([config.TWILIO_ACCOUNT_SID.strip(), config.TWILIO_AUTH_TOKEN.strip(),
                config.TWILIO_WHATSAPP_FROM.strip()]):
            self.notifiers.append(WhatsAppNotifier(
                config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN,
                config.TWILIO_WHATSAPP_FROM, config.PHONE_NUMBER))
        if config.TELEGRAM_BOT_TOKEN.strip():
            self.notifiers.append(TelegramNotifier(config.TELEGRAM_BOT_TOKEN))
        self.alert_listeners = []  # the GUI registers here to show popups
        self._stop = threading.Event()

    # ---- plug-in loading -------------------------------------
    def _load_features(self):
        import features as feat_pkg
        found = []
        for mod_info in pkgutil.iter_modules(feat_pkg.__path__):
            if mod_info.name.startswith("_"):
                continue  # skip _template.py and helpers
            try:
                module = importlib.import_module("features." + mod_info.name)
                for attr in vars(module).values():
                    if (isinstance(attr, type) and issubclass(attr, Feature)
                            and attr is not Feature
                            and attr.__module__ == module.__name__):
                        found.append(attr())
            except Exception:
                print(f"[Could not load feature '{mod_info.name}']")
                traceback.print_exc()
        found.sort(key=lambda f: f.priority)
        return found

    # ---- chat routing ----------------------------------------
    def handle(self, text):
        t = text.strip().lower()
        if not t:
            return "Type something and I'll help!"
        if t in ("hi", "hello", "hey", "namaste"):
            return ("Hey! I'm your Stock Buddy. Ask me things like:\n"
                    "  - 'should I buy reliance?'\n"
                    "  - 'how is the market today?'\n"
                    "  - 'what is a dividend?'\n"
                    "Or press the buttons above the chat box.")
        for f in self.features:
            try:
                if f.can_handle(t):
                    return f.handle(text, self)
            except Exception as e:
                return f"Oops, that feature hit a snag: {e}"
        return ("I didn't quite get that. Try:\n"
                "  - a stock name, like: tata motors\n"
                "  - 'best stocks today'\n"
                "  - 'news'\n"
                "  - 'what is the stock market?'\n"
                "  - 'help' to see everything I can do.")

    def press_button(self, feature):
        return feature.on_button(self)

    def send_raw(self, message):
        """Push a short plain message to every phone channel."""
        for n in self.notifiers:
            try:
                n.send("", message)
            except Exception as e:
                print(f"[Notifier failed: {e}]")
        for listener in self.alert_listeners:
            try:
                listener(message)
            except Exception:
                pass

    def phone_channels(self):
        """Which phone channels are actually switched on right now."""
        channels = []
        if config.SMS_API_KEY.strip():
            channels.append("SMS")
        if all([config.TWILIO_ACCOUNT_SID.strip(), config.TWILIO_AUTH_TOKEN.strip(),
                config.TWILIO_WHATSAPP_FROM.strip()]):
            channels.append("WhatsApp")
        if config.TELEGRAM_BOT_TOKEN.strip():
            channels.append("Telegram" if get_chat_id() else
                            "Telegram (message the bot once first)")
        return channels

    # ---- alerts ----------------------------------------------
    def notify(self, title, message):
        full = f"{title}\n{message}"
        for n in self.notifiers:
            try:
                n.send(title, message)
            except Exception as e:
                print(f"[Notifier failed: {e}]")
        for listener in self.alert_listeners:
            try:
                listener(full)
            except Exception:
                pass

    # ---- background loop -------------------------------------
    def start_background(self):
        def loop():
            while not self._stop.is_set():
                for f in self.features:
                    try:
                        f.tick(self)
                    except Exception:
                        pass  # a background hiccup must never crash the app
                self._stop.wait(60)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def stop(self):
        self._stop.set()
