# ============================================================
#  FEATURE: BEGINNER FRIEND (chat helper)
#  Answers "what is ...?" questions in very simple words and
#  explains what the app can do. Add more words to GLOSSARY
#  any time - it's just a dictionary.
# ============================================================

from core.feature import Feature

GLOSSARY = {
    "stock": "A tiny slice of a company. Buy one share of Reliance and you own a super-small piece of Reliance. If the company does well, your slice usually becomes more valuable.",
    "share": "Same as a stock - one tiny piece of a company.",
    "stock market": "A giant online marketplace where people buy and sell tiny pieces (shares) of companies. Prices go up when more people want to buy, down when more want to sell.",
    "nse": "National Stock Exchange - India's biggest stock marketplace, where you buy in rupees. (BSE is the other big one.)",
    "bse": "Bombay Stock Exchange - India's oldest stock marketplace, in Mumbai.",
    "nifty": "A scoreboard of India's 50 biggest companies. If Nifty is up, most big stocks had a good day. Like the class average, but for stocks.",
    "sensex": "Like Nifty, but a scoreboard of 30 big companies on the BSE.",
    "dividend": "A thank-you payment. Some companies share a bit of their profit with everyone who owns their shares, usually once or twice a year.",
    "ipo": "Initial Public Offering - the day a company first sells its shares to the public. Like a shop's grand opening, but for stocks.",
    "portfolio": "Just the collection of all the stocks you own. Your 'stock basket'.",
    "bull market": "A stretch when prices keep going UP. (A bull attacks by lifting its horns up.)",
    "bear market": "A stretch when prices keep going DOWN. (A bear attacks by swiping its paws down.)",
    "volatility": "How jumpy a stock's price is. High volatility = rollercoaster. Low = calm bus ride.",
    "market cap": "The total price tag of a whole company: share price times number of shares. Big market cap = giant company.",
    "pe ratio": "Price-to-Earnings ratio: how many rupees you pay for each rupee the company earns per year. Lower can mean cheaper, but it's not the whole story. Don't worry about this one yet.",
    "profit": "Money left after a company pays all its bills. More profit usually = healthier company.",
    "loss": "When a company spends more than it earns. A few bad quarters happen; constant losses are a red flag.",
    "broker": "The app/company that lets you buy and sell stocks (like Zerodha, Groww, Angel One). They keep your shares safely, like a bank keeps money.",
    "demat": "A digital locker where your shares are stored. Your broker opens one for you.",
    "stop loss": "An automatic safety rule: 'if this stock falls to X, sell it for me' so a small loss doesn't become a huge one.",
    "intraday": "Buying and selling within the SAME day. Very risky, basically guessing - beginners should stay away.",
    "delivery": "Buying a stock and actually keeping it for days/weeks/years. The calmer, saner way for beginners.",
    "mutual fund": "A basket where many people pool money and a professional picks stocks for everyone. Easier than picking stocks yourself.",
    "sip": "Systematic Investment Plan - investing a fixed small amount every month automatically, like a recurring deposit but into a mutual fund.",
    "index fund": "A cheap mutual fund that just copies a scoreboard like Nifty instead of trying to be clever. A popular beginner choice.",
    "blue chip": "A big, famous, well-run company (Reliance, TCS, HDFC Bank). Generally steadier than small unknown companies.",
    "penny stock": "A very cheap share of a tiny company. Tempting because it's cheap, but super risky - many go to zero. Avoid as a beginner.",
    "52 week high": "The highest price a stock touched in the past year.",
    "52 week low": "The lowest price a stock touched in the past year.",
    "correction": "A drop of around 10% after prices ran up a lot. Normal market breathing, not always a disaster.",
    "crash": "A sudden big fall (20%+). Scary, but markets have recovered from every crash so far. Panic-selling usually locks in losses.",
    "sebi": "Securities and Exchange Board of India - the referee/umpire of the stock market. Makes rules so nobody cheats you.",
    "circuit": "A safety pause. If a stock moves too fast in one day, trading halts briefly so people can cool down.",
    "bonus share": "Free extra shares a company gives existing owners. You own more slices, but the pizza is the same size.",
    "split": "Cutting each share into smaller cheaper shares (like exchanging a Rs.500 note for five Rs.100 notes). Total value stays the same.",
    "order": "Your instruction to the broker: 'buy 2 shares of X at Rs.Y'.",
    "limit order": "An order that only goes through at YOUR price or better. 'Buy only if it drops to Rs.100.'",
    "market order": "An order that buys/sells immediately at whatever the current price is.",
}


class ChatHelp(Feature):
    name = "beginner friend"
    button = None
    priority = 15

    def can_handle(self, text):
        if text in ("help", "what can you do", "commands", "who are you"):
            return True
        if any(q in text for q in ("what is", "what are", "what does",
                                   "what's a", "whats a", "explain",
                                   "meaning of", "mean?", "define")):
            return True
        # Also catch a glossary word asked about directly: "dividend?"
        word = text.strip(" ?.!")
        return word in GLOSSARY

    def handle(self, text, app):
        t = text.lower().strip()
        if t in ("help", "what can you do", "commands", "who are you"):
            return self._help_text(app)

        # Find which glossary word they're asking about (longest first).
        for word in sorted(GLOSSARY, key=len, reverse=True):
            if word in t:
                return f"{word.upper()}, in simple words:\n\n{GLOSSARY[word]}"

        return ("I don't have that word in my mini-dictionary yet.\n"
                "Try asking things like: 'what is a dividend?', "
                "'what is nifty?', 'what is an IPO?'\n"
                "Or ask me about a stock: 'should I buy tata motors?'")

    def _help_text(self, app):
        buttons = [f.button for f in app.features if f.button]
        return (
            "I'm Stock Buddy - your simple Indian stock market helper.\n"
            "\n"
            "BUTTONS: " + " | ".join(buttons) + "\n"
            "\n"
            "THINGS YOU CAN TYPE:\n"
            "  - any stock name: 'reliance', 'tata motors', 'zomato'\n"
            "  - 'should I buy infosys?'\n"
            "  - 'how is the market today?'\n"
            "  - 'best stocks today'\n"
            "  - 'news'\n"
            "  - 'what is a dividend?' (or IPO, Nifty, SIP, broker...)\n"
            "\n"
            "I also watch for big falls while the market is open and\n"
            "alert you automatically. Everything in simple words, promise."
        )
