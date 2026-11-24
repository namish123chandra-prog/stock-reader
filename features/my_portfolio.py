# ============================================================
#  FEATURE: MY STOCKS (memory + daily review)
#  You tell it what you bought, it remembers in portfolio.json,
#  watches those stocks, and sends you a review every morning.
# ============================================================

import datetime
import re

import config
from core.feature import Feature
from core import market, portfolio
from core.analyze import money


def _find_symbol(text):
    sym, _ = market.find_symbol_in(text)
    if sym:
        return sym
    # Fallback for raw symbols typed in a sentence: "I bought 5 TCS"
    known = {s.replace(".NS", "") for s in market.all_watch_symbols()}
    known |= {v for v in market.ALIASES.values() if not v.startswith("^")}
    for word in re.findall(r"[A-Za-z&][A-Za-z&-]{1,15}", text.upper()):
        if word in known:
            return word + ".NS"
    return None


def _numbers(text):
    price_match = re.search(r"(?:at|@|for|price)\s*R?s?\.?\s*"
                            r"(\d+(?:[.,]\d+)?)", text, re.I)
    price = None
    without_price = text
    if price_match:
        price = float(price_match.group(1).replace(",", ""))
        without_price = text[:price_match.start()] + text[price_match.end():]
    qty_match = re.search(r"\b(\d+)\b", without_price)
    qty = int(qty_match.group(1)) if qty_match else 1
    if price is None:
        rest = re.findall(r"\b(\d+)\b", without_price)
        if len(rest) >= 2:
            qty, price = int(rest[0]), float(rest[1])
    return qty, price


class MyPortfolio(Feature):
    name = "my stocks"
    button = "My Stocks"
    priority = 25

    def can_handle(self, text):
        words = ["my portfolio", "my stocks", "stocks i own",
                 "daily review", "review my", "what do i own",
                 "how are my stocks", "how's my portfolio",
                 "clear my portfolio"]
        # "should I buy reliance?" must go to the stock checker, not here.
        # A purchase must start the sentence, like "i bought 5 reliance".
        starts_purchase = text.strip().startswith(
            ("i bought", "i buy", "buy ", "bought ", "add ", "purchased"))
        buy_quantity = re.search(r"\bbuy\s+(\d+|all|my)\b", text)
        sell_quantity = re.search(r"\bsell\s+(\d+|all|my)\b", text)
        starts_sale = text.strip().startswith(("sold ", "sell ")) or (
            text.strip().startswith("remove ") and "alert" not in text)
        return (any(w in text for w in words) or starts_purchase
                or bool(buy_quantity or sell_quantity) or starts_sale)

    def can_handle_buy(self, text):
        return (text.strip().startswith(
            ("i bought", "i buy", "buy ", "bought ", "add ", "purchased"))
            or bool(re.search(r"\bbuy\s+(\d+|all|my)\b", text)))

    def on_button(self, app):
        return portfolio.review_text()

    def handle(self, text, app):
        t = text.strip()

        if "clear my portfolio" in t or "delete my stocks" in t:
            for sym in portfolio.symbols():
                portfolio.sell(sym)
            return "Okay - I've forgotten all the stocks you had saved."

        if ("my portfolio" in t or "my stocks" in t or "stocks i own" in t
                or "daily review" in t or "what do i own" in t
                or "how are my stocks" in t or "how's my portfolio" in t
                or "review" in t):
            return portfolio.review_text()

        sym = _find_symbol(t)
        if not sym:
            return ("Which stock? Say it like: I bought 5 reliance at 1350")

        if any(w in t for w in ["sell ", "sold ", "remove "]):
            qty, _ = _numbers(t)
            left = portfolio.sell(sym, qty if re.search(r"\d", t) else None)
            if left is None:
                return f"You hadn't told me you own {sym.replace('.NS','')}."
            if left == 0:
                return f"Done - I removed {sym.replace('.NS','')} from your stocks."
            return f"Done - you now have {left} shares of {sym.replace('.NS','')} saved."

        if self.can_handle_buy(t):
            qty, price = _numbers(t)
            info = portfolio.add(sym, qty, price)
            price_text = (f" at {money(info['avg_price'])} each" if price else "")
            return (f"Remembered! {info['qty']} shares of "
                    f"{sym.replace('.NS','')}{price_text}. I'll watch it for you "
                    f"and include it in your daily review.\n"
                    "Type 'my stocks' any time to see how it's doing.")

        return portfolio.review_text()

    def tick(self, app):
        """Send the daily review once a day, at DAILY_REVIEW_TIME."""
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        if now.strftime("%H:%M") < config.DAILY_REVIEW_TIME:
            return
        if portfolio.last_review() == today or not portfolio.symbols():
            return
        portfolio.mark_reviewed(today)  # mark first: avoids double messages
        app.notify("Daily Stock Review", portfolio.review_text()[:3500])
