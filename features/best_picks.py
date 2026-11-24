# ============================================================
#  FEATURE: BEST STOCKS TODAY
#  Scores every stock in the watchlist with the same simple
#  rules as "Check a Stock", then shows the top 5.
# ============================================================

from core.feature import Feature
from core import market
from core.analyze import analyze_closes, money, pct


class BestPicks(Feature):
    name = "best stocks"
    button = "Best Stocks Today"
    priority = 30

    def can_handle(self, text):
        phrases = ["best stock", "best pick", "top stock", "which stock",
                   "where should i invest", "what should i buy",
                   "best to buy", "good stocks", "recommend"]
        return any(p in text for p in phrases) or text in ("best", "picks")

    def handle(self, text, app):
        symbols = market.all_watch_symbols()
        bulk = market.get_bulk_closes(symbols, period="1y")
        if not bulk:
            return ("Couldn't download prices right now - check your internet "
                    "and try again in a minute.")

        scored = []
        for sym, closes in bulk.items():
            r = analyze_closes(closes)
            scored.append((sym, r))
        # Best score first; ties broken by smoother (less bumpy) ride.
        scored.sort(key=lambda x: (-x[1]["score"], x[1]["bumpiness"]))

        lines = [
            "TOP 5 LOOKING STOCKS RIGHT NOW",
            f"(I checked {len(bulk)} of India's biggest companies for you)",
            "",
        ]
        for i, (sym, r) in enumerate(scored[:5], 1):
            reason = r["good"][0] if r["good"] else "Steady, nothing scary."
            lines.append(f"{i}. {sym.replace('.NS', '')} - {money(r['price'])} "
                         f"(today {pct(r['today'])})")
            lines.append(f"   Why: {reason}")
            lines.append(f"   Verdict: {r['verdict_short']}")
            lines.append("")
        lines.append("Type any name above to see its full story, risks and precautions.")
        lines.append("")
        lines.append("Honest note: 'best looking' is based on recent price behaviour, "
                     "NOT a promise it will go up. Never invest money you can't "
                     "afford to lose, and chat with a parent/guardian before buying.")
        return "\n".join(lines)
