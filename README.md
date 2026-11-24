# Stock Buddy 🇮🇳

A beginner-friendly **Indian stock market assistant** for the desktop.
It doesn't just chat — it fetches real NSE prices, watches your stocks,
sends alerts, remembers what you bought, and messages your phone.

**Version:** 1.1.0  •  **Made for:** students and first-time investors
**Language:** plain English, no jargon

---

## Run it

Double-click **`Start Stock Buddy.bat`** (or `python run.py`).

First time on a new PC:

```
python -m pip install -r requirements.txt
```

Check everything is installed: `python check_setup.py`

---

## What it can do (18 buttons + chat)

| Button / message | What it does |
|---|---|
| **SOS** | Sends an urgent snapshot of your stocks to your phone channels |
| **News** | Today's market headlines (Economic Times, Moneycontrol, LiveMint) |
| **Today's Market** | Green/red day, biggest winners & losers |
| **My Stocks** | Your saved stocks + profit/loss vs what you paid |
| **Best Stocks Today** | Scores India's 50 biggest companies, shows top 5 |
| **Check a Stock** | BUY / WAIT / SELL, risk, precautions, no jargon |
| **Check Big Drops** | Anything that fell 4%+ today |
| **Send Hi** | Pushes "Hi!" to your phone channels |
| **Phone Chat Setup** | Steps for the free Telegram bot (chat from your phone) |
| **Watchlist** | `watch zomato` / `unwatch zomato` / `my watchlist` |
| **Price Targets** | `alert me if tcs goes above 4500` → notification when crossed |
| **Compare** | `compare reliance vs tcs` → simple side-by-side |
| **SIP Calc** | `5000 per month for 10 years at 12%` → savings growth maths |
| **Close Report** | End-of-day summary, also auto-sent at 3:35 PM IST |
| **Backup** | Creates a dated ZIP of the whole app in `backups/` |
| **Theme** | Dark/light window theme (saved) |
| **Info** | Version, settings, and all file locations |
| **Save Chat** (in app) | Exports the conversation to a text file |
| `I bought 5 reliance at 1350` | Remembers your stock; daily 9 AM report card |
| `sell 2 reliance` | Updates your saved holding |
| `what is a dividend?` | Mini-dictionary (35+ plain-English terms) |
| `help` | Full command list |

### Always-on mode ✅

Double-click **`Turn On Always-On.bat`** once. The app then starts silently
at every Windows logon and keeps watching — no window needed. It sends
big-drop alerts, price-target hits, the 9 AM review and the 3:35 PM close
report. It uses correct **IST** time regardless of your PC's timezone.
Needs the laptop on and logged in. Stop with **`Turn Off Always-On.bat`**.

### Phone notifications

Nothing needed for laptop popups + sound + `alerts_log.txt`. For your phone:

- **Telegram (easiest, free):** message @BotFather → `/newbot` → paste the
  token in `config.py` → restart → message your bot once. Two-way chat works:
  ask it *"how are my stocks going?"* from anywhere.
- **SMS:** free account at fast2sms.com → API key in `config.py`
- **WhatsApp:** free Twilio trial → SID, token and sandbox number in `config.py`

---

## Files (all in the stock-buddy folder)

| File | What's in it |
|---|---|
| `config.py` | Settings, phone number, keys, stock list |
| `portfolio.json` | The stocks you own |
| `watchlist.json` | Stocks you added to watch |
| `targets.json` | Your price alerts |
| `theme.json` | Dark/light choice |
| `alerts_log.txt` | Alert history |
| `app.log` | Startup/error log |
| `backups/` | Dated ZIP backups |
| `features/` | One file per feature — the plug-in system |
| `notifications/` | Laptop, SMS, WhatsApp, Telegram channels |

### Adding a feature (no old code changes)

1. Copy `features/_template.py` → `features/my_feature.py`
2. Fill in `can_handle`, `handle`, and optionally `button` and `tick`
3. Restart — the app finds it and adds its button automatically

New notification channels: add a file in `notifications/` with a
`send(title, message)` method, then add it in `core/app.py`.

---

## Publishing / sharing safely

- **Remove your API keys** from `config.py` before sharing the code. Keys in
  `SMS_API_KEY`, `TWILIO_*` and `TELEGRAM_BOT_TOKEN` are yours.
- `config.py` also has your phone number — change or blank it before sharing.
- `.gitignore` already excludes personal JSON files, logs and backups.
- Press **Backup** (or `python -c "from features.backup import create_backup; print(create_backup())"`)
  before making big changes.
- MIT licence included — you may share and modify this project.

## Honest notes

- Learning helper, **not financial advice**. BUY/WAIT/SELL is a simple price
  check — nobody can promise a stock will rise.
- Free prices can be ~15 minutes delayed. Not for same-day trading.
- Watches India's 50 biggest companies by default; any NSE stock can be
  asked about by name.
- If silent monitor and the window both run, alerts can appear twice.
- If you're in school, involve a parent/guardian before investing real money.
