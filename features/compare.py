# ============================================================
#  FEATURE: COMPARE TWO STOCKS
#  "compare reliance vs tcs" -> simple side-by-side, no jargon.
# ============================================================

import re

from core.feature import Feature
from core import market
from core.analyze import analyze_closes, money, pct


class Compare(Feature):
    name = "compare stocks"
    button = "Compare"
    priority = 39

    def can_handle(self, text):
        return ("compare" in text or " vs " in text or " versus " in text)

    def handle(self, text, app):
        t = text.strip()
        parts = re.split(r"\b(?:vs|versus|and)\b|compare", t, flags=re.I)
        parts = [p.strip(" ?.!") for p in parts if p.strip(" ?.!")]
        symbols = []
        for p in parts:
            sym = market.find_symbol_in(p)[0] or market.resolve_symbol(p)
            if sym:
                symbols.append(sym)
        symbols = list(dict.fromkeys(symbols))[:2]
        if len(symbols) < 2:
            return ("Give me two stocks, like: compare reliance vs tcs")

        rows = []
        for sym in symbols:
            closes = market.get_closes(sym, period="1y")
            if closes is None:
                return f"Couldn't get prices for {sym.replace('.NS','')}."
            rows.append((sym, analyze_closes(closes)))

        lines = ["SIDE-BY-SIDE CHECK", ""]
        for sym, r in rows:
            lines.append(f"{sym.replace('.NS','')}: {money(r['price'])} "
                         f"| today {pct(r['today'])} | month {pct(r['month'])}")
            lines.append(f"   Risk: {r['risk'].split(' - ')[0]}"
                         f" | Verdict: {r['verdict_short']}")
        lines.append("")
        winner = max(rows, key=lambda x: x[1]["score"])
        loser = min(rows, key=lambda x: x[1]["score"])
        if winner[1]["score"] > loser[1]["score"]:
            lines.append(f"Right now, {winner[0].replace('.NS','')} looks "
                         f"stronger than {loser[0].replace('.NS','')}.")
        else:
            lines.append("Both look about equally shaky right now.")
        lines.append("This is a price check, not a promise. "
                     "Type either name for the full story.")
        return "\n".join(lines)
