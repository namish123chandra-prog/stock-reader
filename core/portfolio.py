# ============================================================
#  YOUR STOCK MEMORY
#  Saves the stocks you own in portfolio.json (a tiny text file).
#  Survives closing the app, restarting the PC, everything.
# ============================================================

import json
import os

from core import market
from core.analyze import analyze_closes, money, pct

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "portfolio.json")


def _load():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("holdings", {})
        data.setdefault("last_review", "")
        return data
    except Exception:
        return {"holdings": {}, "last_review": ""}


def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def holdings():
    """Returns {symbol: {"qty": int, "avg_price": float}}"""
    return _load()["holdings"]


def symbols():
    """Just the symbols you own, for the alert watcher."""
    return list(holdings().keys())


def add(symbol, qty, price=None):
    """Add shares. If a price is given, update the average buy price."""
    data = _load()
    h = data["holdings"]
    qty = max(1, int(qty))
    if symbol in h:
        old = h[symbol]
        total_qty = old["qty"] + qty
        if price:
            # weighted average of what you paid
            old["avg_price"] = ((old["avg_price"] * old["qty"] + price * qty)
                                / total_qty)
        elif not old.get("avg_price"):
            old["avg_price"] = 0.0
        old["qty"] = total_qty
    else:
        h[symbol] = {"qty": qty, "avg_price": float(price or 0.0)}
    _save(data)
    return h[symbol]


def sell(symbol, qty=None):
    """Sell all shares of a stock, or just `qty` of them."""
    data = _load()
    h = data["holdings"]
    if symbol not in h:
        return None
    if qty is None or qty >= h[symbol]["qty"]:
        del h[symbol]
        remaining = 0
    else:
        h[symbol]["qty"] -= max(1, int(qty))
        remaining = h[symbol]["qty"]
    _save(data)
    return remaining


def mark_reviewed(date_string):
    data = _load()
    data["last_review"] = date_string
    _save(data)


def last_review():
    return _load()["last_review"]


def review_text():
    """A short, simple daily report card for the stocks you own."""
    h = holdings()
    if not h:
        return ("You haven't told me about any stocks yet. Type something like:\n"
                "  I bought 5 reliance at 1350\n"
                "and I'll remember it and review it for you every day.")
    lines = ["YOUR STOCKS - DAILY REVIEW", ""]
    total_now = total_paid = 0.0
    for sym, info in h.items():
        closes = market.get_closes(sym, period="1y")
        if closes is None:
            lines.append(f"- {sym.replace('.NS', '')}: price not available right now")
            continue
        r = analyze_closes(closes)
        value = info["qty"] * r["price"]
        paid = info["qty"] * info["avg_price"]
        total_now += value
        total_paid += paid
        gain_text = ""
        if paid > 0:
            gain = (value - paid) / paid * 100.0
            gain_text = f", overall {pct(gain)} from what you paid"
        lines.append(f"- {sym.replace('.NS', '')}: {info['qty']} shares, "
                     f"now {money(r['price'])} each (today {pct(r['today'])}"
                     f"{gain_text})")
        lines.append(f"  My take: {r['verdict_short']}")
    lines.append("")
    if total_paid > 0:
        all_gain = (total_now - total_paid) / total_paid * 100.0
        lines.append(f"Your whole basket: {money(total_now)} now vs "
                     f"{money(total_paid)} paid - {pct(all_gain)} overall.")
    lines.append("Type a stock name for the full story and precautions.")
    lines.append("(Learning helper, not guaranteed advice.)")
    return "\n".join(lines)
