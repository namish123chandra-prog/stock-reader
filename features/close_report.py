# ============================================================
#  FEATURE: MARKET CLOSE REPORT
#  A "what happened today" summary at 3:35 PM IST, every weekday.
#  Also available any time with the button.
# ============================================================

import config
from core.feature import Feature
from core.persistence import read_json, write_json
from core.timeutils import is_weekday, now_ist
from features.today_market import TodayMarket

DATE_FILE = "close_report_date.json"


class CloseReport(Feature):
    name = "close report"
    button = "Close Report"
    priority = 72

    def can_handle(self, text):
        return ("close report" in text or "end of day" in text
                or "market closed report" in text or "day summary" in text)

    def handle(self, text, app):
        return TodayMarket().handle("", app)

    def tick(self, app):
        if not is_weekday():
            return
        now = now_ist()
        if now.strftime("%H:%M") < config.CLOSE_REPORT_TIME:
            return
        today = now.strftime("%Y-%m-%d")
        if read_json(DATE_FILE, {}).get("date") == today:
            return
        write_json(DATE_FILE, {"date": today})
        app.notify("Market Close Report", self.handle("", app)[:3500])
