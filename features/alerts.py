# ============================================================
#  FEATURE: BIG DROP ALERTS
#  While the market is open (9:15am - 3:30pm, Mon-Fri), checks
#  the watchlist every few minutes. If a stock falls more than
#  DROP_ALERT_PERCENT in one day, it alerts you:
#   - popup + loud sound on this laptop (always)
#   - real SMS to your phone (if SMS_API_KEY is set in config.py)
#  The button lets you check for big drops right now, any time.
# ============================================================

import time

import config
from core.feature import Feature
from core import market, portfolio
from core.analyze import pct
from core.timeutils import market_open, now_ist


class DropAlerts(Feature):
    name = "drop alerts"
    button = "Check Big Drops"
    priority = 60

    def __init__(self):
        self._last_check = 0.0
        self._alerted = set()
        self._alerted_date = None

    # ---- helpers ---------------------------------------------
    def _market_open(self):
        return market_open()  # proper Indian time, whatever your PC says

    def _scan(self, app, send_alerts):
        # Watch the big 50 AND the stocks the user owns.
        symbols = list(dict.fromkeys(
            market.all_watch_symbols() + portfolio.symbols()))
        moves = market.get_daily_moves(symbols)
        if not moves:
            return None
        drops = [(s, m) for s, m in moves.items()
                 if m["change_pct"] <= -config.DROP_ALERT_PERCENT]
        drops.sort(key=lambda kv: kv[1]["change_pct"])

        today = now_ist().date()
        if self._alerted_date != today:
            self._alerted = set()
            self._alerted_date = today

        if send_alerts:
            for sym, m in drops:
                if sym not in self._alerted:
                    self._alerted.add(sym)
                    app.notify(
                        "BIG DROP ALERT",
                        f"{sym.replace('.NS', '')} is {pct(m['change_pct'])} today "
                        f"(price ~Rs.{m['price']:.0f}). Don't panic - open Stock "
                        f"Buddy and type the name to see what's going on.")
        return drops

    # ---- background watching ----------------------------------
    def tick(self, app):
        if not self._market_open():
            return
        if time.time() - self._last_check < config.CHECK_EVERY_MINUTES * 60:
            return
        self._last_check = time.time()
        self._scan(app, send_alerts=True)

    # ---- button: check right now -------------------------------
    def on_button(self, app):
        drops = self._scan(app, send_alerts=False)
        if drops is None:
            return "Couldn't fetch prices - check your internet and try again."
        if not drops:
            return (f"Good news: no watchlist stock has fallen "
                    f"{config.DROP_ALERT_PERCENT}% or more today.\n"
                    f"I also keep watching automatically while the market is "
                    f"open (9:15am-3:30pm) and will alert you if one does.")
        lines = [f"Stocks down {config.DROP_ALERT_PERCENT}%+ today:"]
        for sym, m in drops:
            lines.append(f"  - {sym.replace('.NS', '')}: {pct(m['change_pct'])} "
                         f"(~Rs.{m['price']:.0f})")
        lines.append("")
        lines.append("Type a name above for the full story before doing anything. "
                     "Big drops are exactly when NOT to panic-sell.")
        return "\n".join(lines)

    def can_handle(self, text):
        return ("alert" in text or "big drop" in text or "crash" in text
                or "falling" in text)

    def handle(self, text, app):
        return self.on_button(app)
