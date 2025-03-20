import logging
import unittest

from unittest.mock import patch, MagicMock, call
from crypto_trading_bot import TradingSession  # Assuming this is your main module


class TestTradingSession(unittest.TestCase):

    def setUp(self):
        """
        Set up logging and test configuration for the trading session.
        """
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.config = {
            "branch_wallet_range": (2, 3),
            "max_parallel_branches": 2,
            "enable_shuffling": False,
            "trading_assets": ["BTC"],
            "position_direction": "long",
            "volume_percentage_range": (10, 20),
            "enable_logs": True,
            "proxy_type": "regular",
        }
