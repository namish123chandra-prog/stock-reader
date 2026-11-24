# ============================================================
#  FEATURE: WATCHLIST MANAGER
#  Add/remove stocks from the watchlist by chatting. Saved in
#  watchlist.json, so your list survives restarts.
# ============================================================

from core.feature import Feature
from core import market
from core.persistence import read_json, write_json

FILE = "watchlist.json"


def _stocks():
    return read_json(FILE, [])


def _save(items):
    write_json(FILE, list(dict.fromkeys(items)))


def _pretty(sym):
    return sym.replace(".NS", "")


def _clean(text, *phrases):
    t = text.strip().lower()
    for p in phrases:
        t = t.replace(p, " ")
    return " ".join(t.split())


class WatchList(Feature):
    name = "watchlist"
    button = "Watchlist"
    priority = 36

    def can_handle(self, text):
        return ("watchlist" in text or text.startswith("watch ")
                or text.startswith("unwatch") or "stop watching" in text
                or ("remove " in text and "alert" not in text))

    def handle(self, text, app):
        t = text.strip().lower()
        items = _stocks()

        if ("unwatch" in t or "stop watching" in t
                or ("remove " in t and "watchlist" in t)):
            name = _clean(t, "unwatch", "stop watching", "remove",
                          "from my watchlist", "from watchlist", "watchlist")
            sym = market.resolve_symbol(name)
            if not sym:
                return "Which stock should I remove? e.g. unwatch zomato"
            sym = sym if sym.endswith(".NS") else sym + ".NS"
            if sym in items:
                items.remove(sym)
                _save(items)
                return f"Removed {_pretty(sym)} from your watchlist."
            return f"{_pretty(sym)} wasn't in your watchlist."

        if ("watch " in t or "add " in t) and "watchlist" not in t:
            name = _clean(t, "please", "add", "watch", "to my watchlist")
            sym = market.resolve_symbol(name)
            if not sym:
                return "Which stock? e.g. watch zomato"
            sym = sym if sym.endswith(".NS") else sym + ".NS"
            if sym in items:
                return f"{_pretty(sym)} is already on your watchlist."
            items.append(sym)
            _save(items)
            return (f"Added {_pretty(sym)}! I'll check it in Today's Market, "
                    "Best Stocks, and drop alerts.")

        lines = [f"YOUR WATCHLIST ({len(items)} stocks you added)"]
        if items:
            for s in items:
                lines.append("  - " + _pretty(s))
        else:
            lines.append("  Nothing yet. Type: watch zomato")
        lines.append("")
        lines.append("Add: watch infosys  |  Remove: unwatch infosys")
        lines.append("Plus the 50 big companies are always watched automatically.")
        return "\n".join(lines)
