# -*- coding: utf-8 -*-
from .context import ztom
from ztom import core
from ztom import errors
import unittest


class CoreFuncTestSuite(unittest.TestCase):

    def test_get_trade_direction_to_currency(self):
        symbol = "ETH/BTC"
        self.assertEqual("buy", core.get_trade_direction_to_currency(symbol, "ETH"))
        self.assertEqual("sell", core.get_trade_direction_to_currency(symbol, "BTC"))
        self.assertEqual(False, core.get_trade_direction_to_currency(symbol, "USD"))

    def test_get_symbol(self):
        markets = dict({"ETH/BTC": True})
        self.assertEqual("ETH/BTC", core.get_symbol("ETH", "BTC", markets))
        self.assertEqual("ETH/BTC", core.get_symbol("BTC", "ETH", markets))
        self.assertEqual(False, core.get_symbol("USD", "ETH", markets))

    def test_order_type(self):
        symbol = "ETH/BTC"
        self.assertEqual("buy", core.get_order_type("BTC", "ETH", symbol))
        self.assertEqual("sell", core.get_order_type("ETH", "BTC", symbol))
        self.assertEqual(False, core.get_order_type("BTC", "USD", symbol))

    def test_get_symbol_order_price_from_tickers(self):

        ticker = {"CUR1/CUR2": {
            "ask": 2,
            "bid": 1
        }}

        # sell
        maker_taker_price = core.get_symbol_order_price_from_tickers("CUR1", "CUR2", ticker)

        self.assertDictEqual(
            {"symbol": "CUR1/CUR2",
             "order_type": "sell",
             "price_type": "bid",
             "price": 1,
             "maker_price_type": "ask",
             "maker_price": 2
             }, maker_taker_price)

        # buy
        maker_taker_price = core.get_symbol_order_price_from_tickers("CUR2", "CUR1", ticker)

        self.assertDictEqual(
            {"symbol": "CUR1/CUR2",
             "order_type": "buy",
             "price_type": "ask",
             "price": 2,
             "maker_price_type": "bid",
             "maker_price": 1
             }, maker_taker_price)




    def test_amount_to_precision(self):
        self.assertEqual(1.399, core.amount_to_precision(1.399, 3))
        self.assertEqual(1, core.amount_to_precision(1.3999))
        self.assertEqual(1, core.amount_to_precision(1.9999))
        self.assertEqual(1.99, core.amount_to_precision(1.9999, 2))

    def test_price_to_precision(self):
        self.assertEqual(1.399, core.price_to_precision(1.399, 3))
        self.assertEqual(1.3999, core.price_to_precision(1.3999))
        self.assertEqual(1.9999, core.price_to_precision(1.9999))
        self.assertEqual(2, core.price_to_precision(1.9999, 2))

    def test_relative_target_price_difference(self):

        self.assertAlmostEqual(0.1, core.relative_target_price_difference("sell", 1, 1.1), 6)
        self.assertAlmostEqual(-0.1, core.relative_target_price_difference("sell", 1, 0.9), 6)

        self.assertAlmostEqual(-0.1, core.relative_target_price_difference("buy", 1, 1.1), 6)
        self.assertAlmostEqual(0.1, core.relative_target_price_difference("buy", 1, 0.9), 6)

        self.assertAlmostEqual(0.3, core.relative_target_price_difference("buy", 1, 0.7), 6)

        self.assertAlmostEqual(0.3, core.relative_target_price_difference("buy", 2, 1.4), 6)
        self.assertAlmostEqual(0.3, core.relative_target_price_difference("buy", 2, 1.4), 6)

        with self.assertRaises(ValueError) as cntx:
            core.relative_target_price_difference("selll", 1, 1.1)

        self.assertEqual(ValueError, type(cntx.exception))

    def test_convert_currency(self):
        # buy side
        dest_amount = core.convert_currency("RUB", 1, "USD", "USD/RUB", price=70)
        self.assertEqual(dest_amount, 1/70)

        # sell side
        dest_amount = core.convert_currency("USD", 1, "RUB", "USD/RUB", price=70)
        self.assertEqual(dest_amount, 70)

        # taker price from ticker sell side
        dest_amount = core.convert_currency("USD", 1, "RUB", symbol="USD/RUB", ticker={"bid": 70})
        self.assertEqual(dest_amount, 70)

        # maker price from ticker sell side
        dest_amount = core.convert_currency("USD", 1, "RUB", symbol="USD/RUB", ticker={"bid": 70, "ask": 71},
                                            taker=False)
        self.assertEqual(dest_amount, 71)

        # taker price from ticker buy side
        dest_amount = core.convert_currency("RUB", 1, "USD", symbol="USD/RUB", ticker={"ask": 71})
        self.assertEqual(dest_amount, 1/71)

        # maker price from ticker buy side
        dest_amount = core.convert_currency("RUB", 1, "USD", symbol="USD/RUB", ticker={"ask": 71, "bid": 70},
                                            taker=False)
        self.assertEqual(dest_amount, 1/70)

        # no ticker or symbol provided
        with self.assertRaises(Exception) as cntx:
            core.convert_currency("RUB", 1, "USD")
        self.assertEqual(Exception, type(cntx.exception))
        self.assertEqual('No symbol or ticker provided', cntx.exception.args[0])

        # no symbol in ticker
        with self.assertRaises(Exception) as cntx:
            core.convert_currency("RUB", 1, "USD", ticker={})
        self.assertEqual(errors.TickerError, type(cntx.exception))
        self.assertEqual('No Symbol in Ticker', cntx.exception.args[0])

        # symbol not contains both currencies
        with self.assertRaises(errors.TickerError) as cntx:
            core.convert_currency("RUB", 1, "USD", symbol="RUB/GBP")
        self.assertEqual(errors.TickerError, type(cntx.exception))
        self.assertEqual('Symbol not contains both currencies', cntx.exception.args[0])

        # zero price
        with self.assertRaises(Exception) as cntx:
            core.convert_currency("RUB", 1, "USD", symbol="RUB/USD", price=0)
        self.assertEqual(Exception, type(cntx.exception))
        self.assertEqual('Zero price', cntx.exception.args[0])

    def test_price_convert_dest_amount(self):

        price = core.ticker_price_for_dest_amount("sell", 1000, 0.32485131)
        self.assertAlmostEqual(price, 0.00032485, 8)

        price = core.ticker_price_for_dest_amount("buy", 1, 70)
        self.assertAlmostEqual(price, 1/70, 8)





if __name__ == '__main__':
    unittest.main()