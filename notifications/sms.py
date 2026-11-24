# ============================================================
#  REAL SMS TO YOUR PHONE (optional)
#  Uses Fast2SMS (an Indian SMS service). To turn it on:
#   1. Sign up at https://www.fast2sms.com
#   2. Put your API key in config.py -> SMS_API_KEY
#  Without a key, this channel stays switched off and laptop
#  alerts still work.
# ============================================================

import requests


class SmsNotifier:
    def __init__(self, api_key, phone_number):
        self.api_key = api_key
        self.phone = phone_number

    def send(self, title, message):
        # Keep it short - SMS costs money per message!
        text = f"{title}: {message}"[:150]
        resp = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": self.api_key},
            data={
                "route": "q",              # quick transactional route
                "message": text,
                "numbers": self.phone,
                "flash": 0,
            },
            timeout=15,
        )
        result = resp.json()
        if not result.get("return"):
            raise RuntimeError(f"SMS not sent: {result}")
