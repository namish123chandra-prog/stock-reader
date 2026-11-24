# ============================================================
#  FEATURE: INFO / SETTINGS
#  Shows the version, where files live, and what's switched on.
# ============================================================

import config
from core.feature import Feature
from core import market, portfolio


class Info(Feature):
    name = "info"
    button = "Info"
    priority = 8   # before the stock checker mistakes "settings" for a ticker

    def can_handle(self, text):
        return any(w in text for w in
                   ["settings", "version", "about", "info", "what files"])

    def handle(self, text, app):
        channels = app.phone_channels() or ["none (laptop alerts only)"]
        return "\n".join([
            f"STOCK BUDDY v{config.VERSION}",
            "",
            f"Stocks watched: {len(market.all_watch_symbols())} "
            f"(50 big ones + {len(market.user_watchlist())} you added)",
            f"Stocks in memory: {len(portfolio.holdings())}",
            f"Phone channels: {', '.join(channels)}",
            f"Big-drop alert: {config.DROP_ALERT_PERCENT}% "
            f"every {config.CHECK_EVERY_MINUTES} min",
            f"Daily review: {config.DAILY_REVIEW_TIME} IST",
            f"Close report: {config.CLOSE_REPORT_TIME} IST",
            "",
            "FILES (all in the stock-buddy folder):",
            "  config.py - settings & phone keys",
            "  portfolio.json - the stocks you own",
            "  watchlist.json - stocks you added to watch",
            "  targets.json - your price alerts",
            "  alerts_log.txt - alert history",
            "  backups/ - dated ZIP backups",
            "",
            "To add a feature: copy features/_template.py and restart.",
        ])
