# ============================================================
#  FEATURE: NEWS BUTTON
#  Pulls today's Indian stock-market headlines from free public
#  RSS feeds (Economic Times, Moneycontrol, LiveMint).
# ============================================================

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import datetime

import requests

from core.feature import Feature

FEEDS = [
    ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Moneycontrol", "https://www.moneycontrol.com/rss/marketreports.xml"),
    ("LiveMint", "https://www.livemint.com/rss/markets"),
]


class News(Feature):
    name = "news"
    button = "News"
    priority = 10

    def can_handle(self, text):
        return "news" in text or "headline" in text

    def handle(self, text, app):
        items = []
        for source, url in FEEDS:
            try:
                resp = requests.get(url, timeout=10,
                                    headers={"User-Agent": "Mozilla/5.0"})
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:8]:
                    title = (item.findtext("title") or "").strip()
                    date_text = item.findtext("pubDate") or ""
                    when = None
                    try:
                        when = parsedate_to_datetime(date_text)
                    except Exception:
                        pass
                    if title:
                        items.append((title, source, when))
            except Exception:
                continue  # one dead feed shouldn't kill the others

        if not items:
            return ("I couldn't reach the news sites right now. "
                    "Check your internet and press News again.")

        # Prefer today's news; keep the newest first.
        today = datetime.date.today()

        def sort_key(it):
            when = it[2]
            is_today = 0 if (when and when.date() == today) else 1
            stamp = when.timestamp() if when else 0
            return (is_today, -stamp)

        items.sort(key=sort_key)
        seen, unique = set(), []
        for it in items:
            key = it[0].lower()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(it)

        lines = ["TODAY'S STOCK MARKET NEWS", ""]
        for i, (title, source, when) in enumerate(unique[:12], 1):
            time_str = when.strftime("%I:%M %p") if when else ""
            lines.append(f"{i}. {title}")
            lines.append(f"   ({source}{' - ' + time_str if time_str else ''})")
        lines.append("")
        lines.append("Want the story behind a headline? Type the company's "
                     "name and I'll show you how its stock is doing.")
        return "\n".join(lines)
