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

    @patch("crypto_trading_bot.time.sleep", return_value=None)
    def test_run_session_success(self, mock_sleep):
        """
        Test that the trading session executes successfully
        when wallets and proxies are available.
        """
        wallet_manager_mock = MagicMock()
        proxy_manager_mock = MagicMock()
        transaction_manager_mock = MagicMock()

        session = TradingSession(self.config)
        session.wallet_manager = wallet_manager_mock
        session.proxy_manager = proxy_manager_mock
        session.transaction_manager = transaction_manager_mock

        mock_wallets = ["wallet_1", "wallet_2", "wallet_3"]
        wallet_manager_mock.wallets = mock_wallets
        wallet_manager_mock.get_next_wallet.side_effect = lambda x: (
            mock_wallets[x] if x < len(mock_wallets) else None
        )

        proxy_manager_mock.get_proxy.side_effect = lambda account_id: {
            "ip_port": f"127.0.0.1:808{account_id}",
            "auth": f"user{account_id}:pass{account_id}",
        }

        transaction_manager_mock.execute_trade.side_effect = (
            lambda wallet, asset, direction, size, proxy: {
                "status": "success",
                "transaction_hash": f"hash_{wallet}",
                "details": {"wallet": wallet, "proxy_used": proxy["ip_port"]},
            }
        )

        session.run_session("branch")
        transaction_manager_mock.execute_trade.assert_called()
