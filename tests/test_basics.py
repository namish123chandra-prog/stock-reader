"""Fast tests that do not need the internet.

Run with:  python -m unittest discover -s tests -v
"""

import datetime
import unittest

import core.timeutils as timeutils
from core.analyze import analyze_closes, money, pct
from core.app import App
from core import market
from features.chart import _draw


class MoneyTests(unittest.TestCase):
    def test_indian_number_format(self):
        self.assertEqual(money(142350.5), "Rs.1,42,350.50")
        self.assertEqual(money(999), "Rs.999.00")
        self.assertEqual(money(-5.5), "-Rs.5.50")

    def test_percent_words(self):
        self.assertEqual(pct(3.2), "up 3.2%")
        self.assertEqual(pct(-0.1), "down 0.1%")


class AnalyzeTests(unittest.TestCase):
    def test_rising_prices_look_good(self):
        closes = [100 + i for i in range(120)]
        report = analyze_closes(closes)
        self.assertGreaterEqual(report["score"], 2)
        self.assertIn("LOOKS GOOD", report["verdict"])

    def test_falling_prices_look_weak(self):
        closes = [220 - i for i in range(120)]
        report = analyze_closes(closes)
        self.assertLess(report["score"], 0)
        self.assertIn("LOOKS WEAK", report["verdict"])

    def test_flat_prices_are_neutral(self):
        report = analyze_closes([100.0] * 120)
        self.assertEqual(report["verdict_short"], "WAIT")


class MarketNameTests(unittest.TestCase):
    def test_friendly_names(self):
        self.assertEqual(market.resolve_symbol("reliance"), "RELIANCE.NS")
        self.assertEqual(market.resolve_symbol("tcs"), "TCS.NS")
        self.assertEqual(market.resolve_symbol("nifty"), "^NSEI")

    def test_find_name_inside_sentence(self):
        symbol, name = market.find_symbol_in("should i buy tata motors?")
        self.assertEqual(symbol, "TMPV.NS")
        self.assertEqual(name, "tata motors")


class TimeTests(unittest.TestCase):
    def setUp(self):
        self.original = timeutils.now_ist

    def tearDown(self):
        timeutils.now_ist = self.original

    def fake_time(self, year, month, day, hour, minute):
        return datetime.datetime(year, month, day, hour, minute,
                                 tzinfo=timeutils.IST)

    def test_market_open_during_weekday(self):
        timeutils.now_ist = lambda: self.fake_time(2026, 11, 24, 10, 0)
        self.assertTrue(timeutils.market_open())

    def test_market_closed_at_night(self):
        timeutils.now_ist = lambda: self.fake_time(2026, 11, 24, 20, 0)
        self.assertFalse(timeutils.market_open())

    def test_market_closed_on_sunday(self):
        timeutils.now_ist = lambda: self.fake_time(2026, 11, 22, 10, 0)
        self.assertFalse(timeutils.market_open())


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = App()
        cls.names = {f.name for f in cls.app.features}
        cls.buttons = [f.button for f in cls.app.features if f.button]

    def test_new_features_are_loaded(self):
        for name in ("price chart", "watchlist", "price targets",
                     "compare stocks", "sip calculator", "close report",
                     "backup", "theme", "info"):
            self.assertIn(name, self.names)

    def test_buttons_are_unique(self):
        self.assertEqual(len(self.buttons), len(set(self.buttons)))
        self.assertIn("Chart", self.buttons)
        self.assertIn("Help", self.buttons)

    def test_chat_routing(self):
        self.assertIn("Stock Buddy", self.app.handle("hi"))
        self.assertIn("DIVIDEND", self.app.handle("what is a dividend?"))
        self.assertIn("BUTTONS", self.app.handle("help"))
        self.assertIn("STOCK BUDDY v", self.app.handle("settings"))
        self.assertIn("chart reliance", self.app.handle("chart"))

    def test_chart_draws_something(self):
        chart = _draw([100, 102, 101, 105, 104])
        self.assertIsNotNone(chart)
        self.assertIn("#", chart)


if __name__ == "__main__":
    unittest.main()
