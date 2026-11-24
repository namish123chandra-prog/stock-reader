# ============================================================
#  FEATURE: SIP / MONEY CALCULATOR
#  "if I put 5000 a month for 10 years at 12%" -> simple maths
#  showing how saving little by little can grow.
# ============================================================

import re

from core.feature import Feature
from core.analyze import money


class SipCalculator(Feature):
    name = "sip calculator"
    button = "SIP Calc"
    priority = 32

    def can_handle(self, text):
        return ("sip" in text or "per month" in text or "a month" in text
                or "compound" in text or "invest 5000" in text)

    def on_button(self, app):
        return ("Type it like:  if I invest 5000 per month for 10 years at 12%\n"
                "I'll show you what that could grow into, in rupees.")

    def handle(self, text, app):
        nums = [float(x.replace(",", "")) for x in
                re.findall(r"\d[\d,]*(?:\.\d+)?", text)]
        if not nums:
            return self.on_button(app)
        monthly = nums[0]
        years = nums[1] if len(nums) > 1 else 10
        rate = nums[2] if len(nums) > 2 else 12
        if monthly <= 0 or years <= 0 or years > 60 or rate > 100:
            return "Those numbers don't look right. Try: 5000 per month for 10 years at 12%"

        months = int(years * 12)
        r = rate / 100 / 12
        future = monthly * (((1 + r) ** months - 1) / r) if r else monthly * months
        invested = monthly * months
        growth = future - invested

        return "\n".join([
            "YOUR SAVINGS GROWTH (simple maths, not a promise)",
            "",
            f"Putting {money(monthly)} every month for {years:g} years:",
            f"  Money you put in: {money(invested)}",
            f"  Could grow to about: {money(future)}",
            f"  Extra growth: {money(growth)}",
            "",
            "This assumes a steady " + f"{rate:g}% a year - real markets jump "
            "up and down, and 12% is NOT guaranteed. Never count on it for "
            "money you'll need soon.",
        ])
