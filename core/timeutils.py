# ============================================================
#  INDIA TIME HELPER
#  Uses IST (UTC+5:30) no matter what timezone your PC is set to.
# ============================================================

import datetime

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def now_ist():
    return datetime.datetime.now(IST)


def market_open():
    now = now_ist()
    if now.weekday() >= 5:          # Saturday / Sunday
        return False
    minutes = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= minutes <= 15 * 60 + 30


def is_weekday():
    return now_ist().weekday() < 5
