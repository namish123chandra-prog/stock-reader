# ============================================================
#  FEATURE: TODAY'S MARKET
#  "How did the market do today?" in plain words.
# ============================================================

from core.feature import Feature
from core import market
from core.analyze import pct


class TodayMarket(Feature):
    name = "today's market"
    button = "Today's Market"
    priority = 20

    def can_handle(self, text):
        phrases = ["market today", "today's market", "todays market",
                   "how is the market", "market doing", "market look",
                   "nifty", "sensex", "market summary"]
        return any(p in text for p in phrases) or text in ("market", "today")

    def handle(self, text, app):
        moves = market.get_daily_moves()
        if not moves:
            return ("I couldn't fetch prices right now. Check your internet "
                    "and try again in a minute.")

        nifty = market.get_closes("^NSEI", period="5d")
        lines = ["TODAY'S MARKET, IN SIMPLE WORDS", ""]
        if nifty is not None and len(nifty) >= 2:
            last, prev = float(nifty.iloc[-1]), float(nifty.iloc[-2])
            ch = (last - prev) / prev * 100.0
            mood = ("a GREEN day - most things went up" if ch > 0.3 else
                    "a RED day - most things went down" if ch < -0.3 else
                    "a flat day - barely moved")
            lines.append(f"The Nifty 50 (India's big-company scoreboard) is "
                         f"{pct(ch)} - so overall it's {mood}.")
            lines.append("")

        ranked = sorted(moves.items(), key=lambda kv: kv[1]["change_pct"], reverse=True)
        ups = [kv for kv in ranked if kv[1]["change_pct"] > 0]
        downs = [kv for kv in ranked if kv[1]["change_pct"] < 0]

        lines.append(f"Of the {len(moves)} big stocks I watch: "
                     f"{len(ups)} went up, {len(downs)} went down.")
        lines.append("")
        lines.append("Biggest WINNERS today:")
        for sym, m in ranked[:3]:
            lines.append(f"  + {sym.replace('.NS', '')}: {pct(m['change_pct'])}")
        lines.append("")
        lines.append("Biggest LOSERS today:")
        for sym, m in ranked[-3:][::-1]:
            lines.append(f"  - {sym.replace('.NS', '')}: {pct(m['change_pct'])}")
        lines.append("")
        lines.append("Tip: type any stock's name to see if it's worth a look.")
        lines.append("(Prices can be ~15 min delayed. Not guaranteed advice.)")
        return "\n".join(lines)
