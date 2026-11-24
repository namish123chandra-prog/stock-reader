# ============================================================
#  FEATURE: SEND HI BUTTON
#  Press it -> "Hi!" gets pushed to your phone number through
#  whichever message channels you've switched on in config.py.
# ============================================================

import config
from core.feature import Feature


class SendHi(Feature):
    name = "send hi"
    button = "Send Hi"
    priority = 90

    def can_handle(self, text):
        return text in ("send hi", "text hi", "say hi", "message hi")

    def on_button(self, app):
        channels = app.phone_channels()
        if not channels:
            return ("No phone channel is switched on yet, so I can't send it.\n"
                    "Easiest fix: get a FREE token from @BotFather on Telegram, "
                    "paste it in config.py (TELEGRAM_BOT_TOKEN), message your "
                    "bot once, then press this button again.\n"
                    "Alternative: put a Fast2SMS API key in config.py "
                    "(SMS_API_KEY) for real SMS.")
        app.send_raw("Hi! - from your Stock Buddy")
        return (f"Sent 'Hi!' to {config.PHONE_NUMBER} via: "
                + ", ".join(channels)
                + "\n(Check your phone. If nothing arrived, the free service "
                  "may need one more setup step from its website.)")

    def handle(self, text, app):
        return self.on_button(app)
