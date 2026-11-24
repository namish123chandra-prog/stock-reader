# ============================================================
#  FEATURE: CHECK A STOCK
#  Type a stock name -> price, simple story, BUY/WAIT/SELL,
#  risks and precautions. No big words.
# ============================================================

from core.feature import Feature
from core import market
from core.analyze import analyze_closes, money, pct


class StockCheck(Feature):
    name = "check a stock"
    button = "Check a Stock"
    priority = 40

    def can_handle(self, text):
        sym, _ = market.find_symbol_in(text)
        if not sym:
            return False
        # A bare stock name always counts ("reliance").
        if len(text.split()) <= 3:
            return True
        intent = ["buy", "sell", "check", "analyse", "analyze", "risk",
                  "should", "about", "invest", "good", "safe", "hold",
                  "precaution", "tell me"]
        return any(w in text for w in intent)

    def on_button(self, app):
        return ("Just type the stock's name in the chat box, like:\n"
                "  reliance   |   tata motors   |   zomato   |   IRCTC\n"
                "You can also ask: 'should I buy infosys?'")

    def handle(self, text, app):
        sym, matched = market.find_symbol_in(text)
        if not sym:
            sym = market.resolve_symbol(text)
        if not sym:
            return "Which stock? Type its name, like 'tata motors'."

        closes = market.get_closes(sym, period="1y")
        if closes is None:
            return (f"Hmm, I couldn't find prices for '{matched or text}'. "
                    "Maybe check the spelling? Use the NSE name, like "
                    "'reliance' or 'tatasteel'.")

        r = analyze_closes(closes)
        name = market.get_company_name(sym)
        pretty = sym.replace(".NS", "")

        lines = [
            f"{pretty} - {name}",
            f"Price right now: about {money(r['price'])}",
            "",
            f"Today: {pct(r['today'])}   |   This week: {pct(r['week'])}",
            f"This month: {pct(r['month'])}   |   Last 3 months: {pct(r['three_months'])}",
            f"Past year: lowest {money(r['year_low'])}, highest {money(r['year_high'])}",
            "",
            f"MY SIMPLE TAKE:  {r['verdict']}",
            "",
            "Why I say that:",
        ]
        for g in r["good"]:
            lines.append("  + " + g)
        for b in r["bad"]:
            lines.append("  - " + b)
        if not r["good"] and not r["bad"]:
            lines.append("  Nothing strong either way - pretty quiet stock.")
        lines += ["", f"RISK: {r['risk']}", "", "PRECAUTIONS:"]
        for p in r["precautions"]:
            lines.append("  * " + p)
        lines.append("")
        lines.append("Remember: I'm a study helper, not a fortune teller. "
                     "Big money decisions? Talk to a parent/guardian first.")
        return "\n".join(lines)
