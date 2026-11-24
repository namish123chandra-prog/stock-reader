# ============================================================
#  FEATURE: SIMPLE PRICE CHART
#  Type "chart reliance" and get a tiny text chart of the last
#  30 trading days. No image files, no extra libraries.
# ============================================================

from core.feature import Feature
from core import market
from core.analyze import money, pct

WIDTH = 42
HEIGHT = 10


def _clean_name(text):
    """Remove the command word and keep the stock name."""
    t = text.strip().lower()
    for word in ("chart", "graph", "trend", "show me", "please"):
        t = t.replace(word, " ")
    return " ".join(t.split())


def _draw(closes):
    """Turn a list of prices into a small ASCII line chart."""
    prices = [float(p) for p in closes][-WIDTH:]
    if len(prices) < 2:
        return None

    low, high = min(prices), max(prices)
    span = high - low or 1.0

    # rows[0] is the top of the chart.
    rows = [[" "] * len(prices) for _ in range(HEIGHT)]

    def row_for(price):
        return min(HEIGHT - 1, max(0, int((high - price) / span * (HEIGHT - 1))))

    previous = row_for(prices[0])
    for column, price in enumerate(prices):
        current = row_for(price)
        # Fill the gap between points so the line looks continuous.
        step = 1 if current >= previous else -1
        for r in range(previous, current + step, step):
            if 0 <= r < HEIGHT:
                rows[r][column] = "#"
        previous = current

    lines = []
    for i, row in enumerate(rows):
        if i == 0:
            label = money(high)
        elif i == HEIGHT - 1:
            label = money(low)
        else:
            label = ""
        lines.append(f"{label:>12} |" + "".join(row))
    lines.append(" " * 12 + " +" + "-" * len(prices))
    lines.append(" " * 14 + "oldest" + " " * max(1, len(prices) - 16) + "today")
    return "\n".join(lines)


class Chart(Feature):
    name = "price chart"
    button = "Chart"
    priority = 34   # before the stock checker treats "chart" as a ticker

    def can_handle(self, text):
        return (text.startswith(("chart ", "graph ", "trend "))
                or text in ("chart", "graph", "trend"))

    def on_button(self, app):
        return ("Type it like:  chart reliance\n"
                "I'll draw the last 30 trading days in the chat, "
                "so you can see the shape at a glance.")

    def handle(self, text, app):
        name = _clean_name(text)
        sym, matched = market.find_symbol_in(name)
        if not sym:
            sym = market.resolve_symbol(name)
        if not sym:
            return self.on_button(app)

        closes = market.get_closes(sym, period="3mo")
        if closes is None:
            return (f"Couldn't get a chart for '{matched or name}'. "
                    "Check the spelling and try again.")

        prices = [float(p) for p in closes]
        chart = _draw(prices)
        if chart is None:
            return "Not enough price history for a chart yet. Try another stock."

        first, last = prices[-min(30, len(prices))], prices[-1]
        change = (last - first) / first * 100.0 if first > 0 else 0.0
        pretty = sym.replace(".NS", "")

        return "\n".join([
            f"CHART: {pretty} - last {min(30, len(prices))} trading days",
            "",
            chart,
            "",
            f"Now: {money(last)}   |   Over this window: {pct(change)}",
            "A chart shows the shape, not the future. Type the stock name "
            "for the full check with risks and precautions.",
        ])
