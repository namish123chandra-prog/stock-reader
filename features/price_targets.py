# ============================================================
#  FEATURE: PRICE TARGET ALERTS
#  "alert me if reliance goes above 1500" -> gets a notification
#  the moment it crosses (checked with every price refresh).
# ============================================================

import re

from core.feature import Feature
from core import market
from core.analyze import money
from core.persistence import read_json, write_json
from core.timeutils import now_ist

FILE = "targets.json"


def _data():
    d = read_json(FILE, {})
    d.setdefault("targets", [])
    return d


class PriceTargets(Feature):
    name = "price targets"
    button = "Price Targets"
    priority = 37

    def can_handle(self, text):
        return ("alert me if" in text or "tell me if" in text
                or "notify me if" in text or "price target" in text
                or "my alerts" in text or "list alerts" in text
                or "remove alert" in text or "clear alerts" in text
                or text in ("targets", "my targets"))

    def _listing(self):
        items = _data()["targets"]
        lines = [f"YOUR PRICE TARGETS ({len(items)})"]
        for i, t in enumerate(items, 1):
            status = "DONE - already crossed" if t.get("done") else "watching"
            lines.append(f"{i}. {t['symbol'].replace('.NS','')} "
                         f"{t['direction']} {money(t['price'])} - {status}")
        lines.append("")
        lines.append("Set one: alert me if tcs goes above 4500")
        lines.append("Remove: remove alert tcs  |  Clear all: clear alerts")
        return "\n".join(lines)

    def handle(self, text, app):
        t = text.strip().lower()

        if "clear alerts" in t:
            write_json(FILE, {"targets": []})
            return "All price targets cleared."
        if "remove alert" in t or "delete alert" in t:
            sym, _ = market.find_symbol_in(t)
            data = _data()
            before = len(data["targets"])
            data["targets"] = [x for x in data["targets"]
                               if x["symbol"] != sym]
            write_json(FILE, data)
            return ("Removed." if len(data["targets"]) < before
                    else "No matching target found.")
        if ("my alerts" in t or "list alerts" in t or "price target" in t
                or t in ("targets", "my targets")):
            return self._listing()

        sym, _ = market.find_symbol_in(t)
        price_match = re.search(r"([\d,]+(?:\.\d+)?)\s*$", t.strip(" ?.!"))
        if not sym or not price_match:
            return ("Tell me like this: alert me if reliance goes above 1500")
        price = float(price_match.group(1).replace(",", ""))
        direction = "below" if any(w in t for w in
                                   ["below", "falls", "drops", "under"]) else "above"
        data = _data()
        data["targets"].append({
            "symbol": sym, "direction": direction,
            "price": price, "done": False,
            "set_on": now_ist().strftime("%Y-%m-%d"),
        })
        write_json(FILE, data)
        return (f"Saved! I'll alert you when {sym.replace('.NS','')} goes "
                f"{direction} {money(price)}. Type 'my alerts' to see them.")

    def tick(self, app):
        targets = _data()["targets"]
        pending = [t for t in targets if not t.get("done")]
        if not pending:
            return
        symbols = list(dict.fromkeys(t["symbol"] for t in pending))
        moves = market.get_daily_moves(symbols)
        if not moves:
            return
        changed = False
        for t in pending:
            m = moves.get(t["symbol"])
            if not m:
                continue
            price = m["price"]
            hit = (price >= t["price"] if t["direction"] == "above"
                   else price <= t["price"])
            if hit:
                t["done"] = True
                changed = True
                app.notify(
                    "PRICE TARGET HIT",
                    f"{t['symbol'].replace('.NS','')} is now {money(price)} - "
                    f"it crossed your {t['direction']} {money(t['price'])} target. "
                    "Type its name for a fresh check.")
        if changed:
            write_json(FILE, {"targets": targets})
