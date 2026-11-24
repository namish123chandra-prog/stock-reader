# ============================================================
#  STOCK BUDDY - SETTINGS
#  Everything you might want to change is in this one file.
# ============================================================

VERSION = "1.1.0"   # bump this when you add a feature

# Your phone number (used for drop alerts). Add YOUR number when you set up
# SMS/WhatsApp/Telegram. Left blank here so this file is safe to publish.
PHONE_NUMBER = ""

# --- SMS alerts -------------------------------------------------
# Real SMS needs a (cheap) SMS service. Easiest in India: Fast2SMS.
# 1. Make a free account at https://www.fast2sms.com
# 2. Copy your API key from their dashboard
# 3. Paste it below between the quotes, save, restart the app.
# Leave it empty ("") and alerts will instead pop up LOUDLY on
# this laptop and get saved in alerts_log.txt.
SMS_API_KEY = ""

# --- WhatsApp (optional, outgoing messages like Hi / SOS / alerts) ---
# Needs a free Twilio trial account: https://www.twilio.com/try-twilio
# Get a WhatsApp-enabled sender number, then fill these in.
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_WHATSAPP_FROM = ""   # e.g. "whatsapp:+14155238886"

# --- Phone chat (recommended! free, works both ways) ---
# 1. In Telegram, message @BotFather, send /newbot, choose a name
# 2. Copy the token it gives you into TELEGRAM_BOT_TOKEN
# 3. Message your new bot once from your phone, then it will answer
#    things like "how are my stocks going?" from anywhere.
TELEGRAM_BOT_TOKEN = ""

# --- Drop alerts ------------------------------------------------
# If a stock in the watchlist falls this much % in ONE day,
# you get an alert. 4.0 means "fell 4% or more today".
DROP_ALERT_PERCENT = 4.0

# How often to check prices while the market is open (minutes)
CHECK_EVERY_MINUTES = 5

# Daily portfolio review time (24-hour clock, India time).
# Example: "09:00" = 9 in the morning, before the market opens.
DAILY_REVIEW_TIME = "09:00"

# Market-close summary time (after the 3:30 PM close)
CLOSE_REPORT_TIME = "15:35"

# --- Stocks we watch --------------------------------------------
# These are India's 50 biggest companies (the "Nifty 50").
# You can check ANY Indian stock by typing its name in the chat,
# even if it is not in this list.
WATCHLIST = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY",
    "BHARTIARTL", "SBIN", "LT", "ITC", "HINDUNILVR",
    "KOTAKBANK", "AXISBANK", "BAJFINANCE", "ASIANPAINT", "MARUTI",
    "HCLTECH", "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO",
    "NTPC", "POWERGRID", "ONGC", "TMPV", "TATASTEEL",
    "JSWSTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA", "BAJAJFINSV",
    "BAJAJ-AUTO", "HEROMOTOCO", "DRREDDY", "CIPLA", "DIVISLAB",
    "APOLLOHOSP", "EICHERMOT", "GRASIM", "HINDALCO", "INDUSINDBK",
    "TECHM", "NESTLEIND", "BRITANNIA", "TATACONSUM", "SBILIFE",
    "HDFCLIFE", "BPCL", "TMCV", "TRENT", "BEL",
]

# Add your own stocks here, like: EXTRA_STOCKS = ["ZOMATO", "IRCTC"]
EXTRA_STOCKS = []

# Prices are remembered for this many minutes so the app stays fast.
# (Free price data can also be ~15 minutes behind the real market.)
CACHE_MINUTES = 15
