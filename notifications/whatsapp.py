# ============================================================
#  WHATSAPP ALERTS (outgoing: Hi, SOS, big drops, daily review)
#  Uses Twilio's free trial. Fill in the TWILIO_* settings in
#  config.py to switch this on. No extra library needed.
# ============================================================

import requests


def indian_number(number):
    """Turn a 10-digit Indian mobile number into +91XXXXXXXXXX."""
    n = "".join(c for c in str(number) if c.isdigit())
    if len(n) == 10:
        n = "91" + n
    return "+" + n


class WhatsAppNotifier:
    def __init__(self, sid, token, from_number, to_number):
        self.sid = sid
        self.token = token
        self.sender = from_number if from_number.startswith("whatsapp:") \
            else "whatsapp:" + from_number
        self.recipient = "whatsapp:" + indian_number(to_number)
        self.url = (f"https://api.twilio.com/2010-04-01/Accounts/"
                    f"{sid}/Messages.json")

    def send(self, title, message):
        resp = requests.post(
            self.url,
            auth=(self.sid, self.token),
            data={"From": self.sender, "To": self.recipient,
                  "Body": f"{title}: {message}"[:1200]},
            timeout=20,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"WhatsApp failed: {resp.text[:200]}")
