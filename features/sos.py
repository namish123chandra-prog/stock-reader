# ============================================================
#  FEATURE: SOS BUTTON
#  Press it -> an urgent message with a quick snapshot of your
#  stocks goes to your phone through all switched-on channels.
# ============================================================

from core.feature import Feature
from core import market, portfolio


class Sos(Feature):
    name = "sos"
    button = "SOS"
    priority = 5   # answer before the stock checker guesses "SOS" is a ticker

    def can_handle(self, text):
        return "sos" in text or "emergency message" in text

    def on_button(self, app):
        lines = ["SOS! This is Stock Buddy - here's your quick snapshot."]
        h = portfolio.holdings()
        if h:
            moves = market.get_daily_moves()
            for sym in h:
                m = moves.get(sym)
                if m:
                    lines.append(f"{sym.replace('.NS','')}: "
                                 f"{'up' if m['change_pct']>=0 else 'down'} "
                                 f"{abs(m['change_pct']):.1f}% today")
                else:
                    lines.append(f"{sym.replace('.NS','')}: price not available")
        else:
            lines.append("You haven't added any stocks to remember yet.")
        lines.append("Open Stock Buddy to see the full review.")
        message = "\n".join(lines)
        app.notify("SOS", message)
        channels = app.phone_channels()
        if not channels:
            return (message + "\n\nNOTE: This only showed on the laptop because "
                    "no phone channel is set up. Add a Telegram bot token in "
                    "config.py to get SOS on your phone too.")
        return "SOS sent to your phone via: " + ", ".join(channels)

    def handle(self, text, app):
        return self.on_button(app)
