# ============================================================
#  SIMPLE ANALYSIS BRAIN
#  Turns a list of daily prices into a beginner-friendly verdict.
#  No fancy jargon - just a few sensible checks, each explained.
#  NOTE: This is a learning helper, NOT guaranteed advice.
# ============================================================


def money(x):
    """Format a number as rupees, Indian style: 1,42,350.50"""
    neg = x < 0
    x = abs(x)
    whole = int(x)
    paise = round((x - whole) * 100)
    if paise == 100:
        whole += 1
        paise = 0
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    out = f"Rs.{s}.{paise:02d}"
    return "-" + out if neg else out


def pct(x):
    return f"{'up' if x >= 0 else 'down'} {abs(x):.1f}%"


def analyze_closes(closes):
    """Look at daily closing prices (oldest first) and return a
    simple report dict. `closes` is a pandas Series."""
    prices = [float(p) for p in closes]
    price = prices[-1]
    n = len(prices)

    def change_over(days):
        if n > days:
            old = prices[-1 - days]
            return (price - old) / old * 100.0 if old > 0 else 0.0
        return 0.0

    today = change_over(1)
    week = change_over(5)
    month = change_over(21)
    three_months = change_over(63)

    year_high = max(prices)
    year_low = min(prices)
    avg50 = sum(prices[-50:]) / min(50, n)

    # "Bumpiness": how much the price jumps around day to day.
    daily_changes = []
    for i in range(max(1, n - 60), n):
        if prices[i - 1] > 0:
            daily_changes.append((prices[i] - prices[i - 1]) / prices[i - 1] * 100.0)
    if daily_changes:
        mean = sum(daily_changes) / len(daily_changes)
        bumpiness = (sum((c - mean) ** 2 for c in daily_changes)
                     / len(daily_changes)) ** 0.5
    else:
        bumpiness = 0.0

    from_high = (price - year_high) / year_high * 100.0  # 0 or negative

    # ---- Score it with simple, explainable rules ----
    score = 0
    good, bad = [], []

    if price > avg50:
        score += 1
        good.append("The price is above its average of the last 50 days - "
                    "it has been climbing, not sinking.")
    else:
        score -= 1
        bad.append("The price is below its average of the last 50 days - "
                   "it has been sliding lately.")

    if month > 3:
        score += 1
        good.append(f"It gained {month:.1f}% in about a month - nice momentum.")
    elif month < -8:
        score -= 1
        bad.append(f"It lost {abs(month):.1f}% in about a month - that's a rough patch.")

    if from_high > -5:
        score += 1
        good.append("It's near its highest price of the past year - buyers are keen.")
    elif from_high < -25:
        score -= 1
        bad.append(f"It's {abs(from_high):.0f}% below its best price of the past year - "
                   "something has been going wrong.")

    if bumpiness > 3:
        score -= 1
        bad.append("The price jumps around a LOT day to day - a bumpy, risky ride.")

    if today < -4:
        score -= 1
        bad.append(f"Today alone it fell {abs(today):.1f}% - be extra careful right now.")

    # ---- Verdict in plain words ----
    if score >= 2:
        verdict = "LOOKS GOOD - a small buy could be okay"
        verdict_short = "BUY (small amount)"
    elif score >= 0:
        verdict = "NEUTRAL - better to WAIT and watch for now"
        verdict_short = "WAIT"
    else:
        verdict = "LOOKS WEAK - avoid buying now; if you own it, think about selling"
        verdict_short = "AVOID / SELL"

    # ---- Risk level ----
    if bumpiness > 3 or from_high < -25:
        risk = "HIGH - this one can swing sharply. Only money you can afford to lose."
    elif bumpiness > 1.8 or from_high < -12:
        risk = "MEDIUM - normal ups and downs. Don't put everything into it."
    else:
        risk = "LOW-ish - fairly steady, but NO stock is ever risk-free."

    # ---- Precautions ----
    precautions = [
        "Never put all your money in one stock - spread it out.",
        "Only invest money you won't need for the next 1-2 years.",
        "This is a simple computer check, not a promise. Markets can surprise anyone.",
    ]
    if bumpiness > 3:
        precautions.append("Because it's so jumpy, start with a very small amount if at all.")
    if from_high > -5:
        precautions.append("It's already near its peak - don't buy just because it's rising fast.")
    if from_high < -25:
        precautions.append("A big fall can mean real trouble inside the company. "
                           "Cheap is not always a bargain.")

    return {
        "price": price, "today": today, "week": week, "month": month,
        "three_months": three_months, "year_high": year_high,
        "year_low": year_low, "from_high": from_high,
        "bumpiness": bumpiness, "score": score,
        "good": good, "bad": bad,
        "verdict": verdict, "verdict_short": verdict_short,
        "risk": risk, "precautions": precautions,
    }
