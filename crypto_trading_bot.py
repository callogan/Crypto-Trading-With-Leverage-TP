import hmac
import hashlib
import logging
import os
import random
import requests
import time

from base64 import b64encode
from datetime import datetime
from typing import List, Dict, Any

from csv_writer import CSVWriter
from config import logger, TRADING_CONFIG, USER_AGENTS


# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WalletManager:
    def __init__(self, keys_file: str = "wallet_keys.txt"):
        self.keys_file = keys_file
        self.wallets = self._load_wallets()
        if not self.wallets:  # Checking the available wallets after downloading
            logger.error("[ERROR] No available wallets fro making transactions.")
        logger.info(f"Loaded wallets: {self.wallets}")

    def _load_wallets(self) -> List[str]:
        """Load wallet private keys from file"""
        if not os.path.exists(self.keys_file):
            logger.warning(f"Wallet file {self.keys_file} not found.")
            return []

        with open(self.keys_file, "r") as f:
            wallets = [line.strip() for line in f if line.strip()]
            logger.info(f"Wallets loaded: {wallets}")
            return wallets

    def add_wallet(self, private_key: str):
        """Add new wallet to the list"""
        with open(self.keys_file, "a") as f:
            f.write(f"{private_key}\n")
        self.wallets.append(private_key)
        logger.info(f"Added wallet: {private_key}")

    def get_next_wallet(self, index: int) -> str:
        """Get next wallet from the list"""
        if 0 <= index < len(self.wallets):
            return self.wallets[index]
        return None


class ProxyManager:
    def __init__(self, proxy_file: str, proxy_type: str = "regular"):
        self.proxy_file = proxy_file
        self.proxy_type = proxy_type
        self.proxies = self._load_proxies()
        if not self.proxies:
            logger.error("[ERROR] No available proxy servers.")
        logger.info(f"Loaded proxies: {self.proxies}")


    def _load_proxies(self) -> List[Dict]:
        """Load proxies from file"""
        with open(self.proxy_file, "r") as f:
            proxies = []
            for line in f:
                if "|" in line:  # Mobile proxy
                    proxy_data, refresh_link = line.strip().split("|")
                    ip_port, auth = proxy_data.split("@")
                    proxies.append(
                        {"ip_port": ip_port, "auth": auth, "refresh_link": refresh_link}
                    )
                else:  # Regular proxy
                    ip_port, auth = line.strip().split("@")
                    proxies.append({
                        'ip_port': ip_port,
                        'auth': auth
                    })
            logger.info(f"Proxies loaded: {proxies}")
            return proxies

    def get_proxy(self, account_id: int) -> Dict:
        """Get proxy for specific account"""
        proxy = self.proxies[account_id % len(self.proxies)]
        logger.info(f"Using proxy for account {account_id}: {proxy}")
        if self.proxy_type == "mobile" and "refresh_link" in proxy:
            requests.get(proxy["refresh_link"])
            logger.info(f"Refreshed mobile proxy: {proxy['refresh_link']}")
        return proxy


class TransactionManager:
    """Handles trading transactions without Web3 dependency"""

    def __init__(self):
        self.user_agents = USER_AGENTS

    def get_random_user_agent(self) -> str:
        """Get user agent generated randomly"""
        user_agent = random.choice(self.user_agents)
        logger.info(f"Selected user agent: {user_agent}")
        return user_agent

    def _generate_signature(self, private_key: str, message: str) -> str:
        """Generate transaction signature"""
        key = bytes.fromhex(private_key.replace("0x", ""))
        message_bytes = message.encode("utf-8")
        signature = hmac.new(key, message_bytes, hashlib.sha256).digest()
        return b64encode(signature).decode("utf-8")

    def execute_trade(
        self, wallet_key: str, asset: str, direction: str, size: float, proxy: Dict
    ) -> Dict[str, Any]:
        """Execute trade with given parameters"""
        try:
            # Generate transaction ID
            tx_id = f"tx_{int(time.time())}_{random.randint(1000, 9999)}"
            logger.info(f"Executing trade: {tx_id} for {wallet_key} - {direction} {size} of {asset}")

            # Simulate transaction validation
            if size > 10000:
                logger.warning(f"Trade failed for {wallet_key}: Insufficient balance")
                return {
                    "status": "failed",
                    "error": "Insufficient balance",
                    "timestamp": datetime.now().isoformat(),
                    "tx_id": tx_id,
                }

            # Simulate transaction processing delay
            time.sleep(random.uniform(0.5, 2.0))

            # Generate signature
            message = f"{tx_id}:{asset}:{direction}:{size}"
            signature = self._generate_signature(wallet_key, message)

            logger.info(f"Trade executed successfully: {tx_id}")
            return {
                "status": "success",
                "transaction_hash": tx_id,
                "signature": signature,
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "asset": asset,
                    "direction": direction,
                    "size": size,
                    "wallet": wallet_key[:10] + "...",
                },
            }

        except Exception as e:
            logger.error(f"Trade execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class TradingSession:
    def __init__(self, config: Dict):
        self.config = config
        self.wallet_manager = WalletManager(config.get("keys_file", "wallet_keys.txt"))
        self.proxy_manager = ProxyManager(
            config.get("proxy_file", "proxies.txt"), config.get("proxy_type", "regular")
        )
        self.transaction_manager = TransactionManager()
        self.setup_logging()
        self.csv_writer = CSVWriter()
        self.active_branches = 0
        self.thread_count = config.get("thread_count", 10)

    def setup_logging(self):
        """Setup logging configuration"""
        if self.config.get('enable_logs', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"trading_{len(self.wallet_manager.wallets)}_{timestamp}.txt"
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            logger.addHandler(file_handler)

    def execute_branch_trading(self):
        """Execute trading with branches"""
        branch_range = self.config.get("branch_wallet_range", (2, 5))
        max_branches = self.config.get("max_parallel_branches", 5)

        wallets = self.wallet_manager.wallets.copy()
        if self.config.get("enable_shuffling", True):
            random.shuffle(wallets)

        self.active_branches = 0
        while wallets and self.active_branches < max_branches:
            branch_size = random.randint(*branch_range)
            if len(wallets) < branch_size:
                break

            branch_wallets = wallets[:branch_size]
            wallets = wallets[branch_size:]

            # Split into long and short positions
            long_count = random.randint(1, branch_size - 1)
            short_count = branch_size - long_count

            self._process_branch(branch_wallets, long_count, short_count)
            self.active_branches += 1

    def execute_parallel_trading(self):
        """Execute trading in parallel threads"""
        thread_count = self.config.get("thread_count", 10)
        delay_range = self.config.get("launch_delay", (0, 3600))

        wallets = self.wallet_manager.wallets.copy()
        if self.config.get("enable_shuffling", True):
            random.shuffle(wallets)

        for i in range(0, len(wallets), thread_count):
            batch = wallets[i : i + thread_count]
            for wallet in batch:
                delay = random.uniform(delay_range[0], delay_range[1])
                time.sleep(delay)
                self._process_wallet(wallet)

    def _process_wallet(self, wallet_key: str):
        """Process individual wallet"""
        if not self.wallet_manager.wallets:
            return

        wallet_index = self.wallet_manager.wallets.index(wallet_key)
        wallet = self.wallet_manager.get_next_wallet(wallet_index)
        if not wallet:
            logger.error(f"[ERROR] Wallet with the index {wallet_index} was not found.")
            return

        proxy = self.proxy_manager.get_proxy(wallet_index)

        # Execute trade based on configuration
        asset = random.choice(self.config.get("trading_assets", ["BTC", "ETH", "SOL"]))
        direction = self._get_trade_direction()
        size = self._get_trade_size()

        result = self.transaction_manager.execute_trade(
            wallet_key, asset, direction, size, proxy
        )

        # Record trade result using CSVWriter
        trade_data = {
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'wallet': wallet_key,
            'direction': direction,
            'size': size,
            'status': result.get('status', 'unknown'),
            'active_branches': self.active_branches,
            'thread_count': self.thread_count,
            'transaction_hash': result.get('transaction_hash', ''),
            'error': result.get('error', '')
        }
        self.csv_writer.record_trade(trade_data)

        if self.config.get('enable_logs', True):
            logger.info(f"Wallet {wallet_key[:8]}: {result}")

    def _process_branch(self, wallets: List[str], long_count: int, short_count: int):
        """Process branch of wallets"""
        total_size = self._get_trade_size()

        # Process long positions
        if long_count > 0:
            long_size = total_size / long_count
            for wallet in wallets[:long_count]:
                self._process_wallet_with_size(wallet, "long", long_size)

        # Process short positions
        if short_count > 0:
            short_size = total_size / short_count
            for wallet in wallets[long_count:]:
                self._process_wallet_with_size(wallet, "short", short_size)

    def _get_trade_direction(self) -> str:
        """Determine trade direction based on configuration"""
        direction_config = self.config.get("position_direction", "random")
        if direction_config == "random":
            return random.choice(["long", "short"])
        return direction_config

    def _get_trade_size(self) -> float:
        """Determine trade size based on configuration"""
        volume_range = self.config.get("volume_percentage_range", (10, 50))
        return random.uniform(*volume_range)

    def _process_wallet_with_size(
        self, wallet: str, direction: str, size: float
    ) -> Dict[str, Any]:
        """Process wallet with specific size and return result"""
        proxy = self.proxy_manager.get_proxy(self.wallet_manager.wallets.index(wallet))
        asset = random.choice(self.config.get("trading_assets", ["BTC", "ETH", "SOL"]))

        result = self.transaction_manager.execute_trade(
            wallet, asset, direction, size, proxy
        )

        # Record trade result to CSV
        self.csv_writer.record_trade({
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'wallet': wallet,
            'direction': direction,
            'size': size,
            'status': result.get('status', 'unknown'),
            'active_branches': self.active_branches,
            'thread_count': self.thread_count,
            'transaction_hash': result.get('transaction_hash', ''),
            'error': result.get('error', '')
        })

        if self.config.get('enable_logs', True):
            logger.info(f"Branch trade - Wallet {wallet[:8]}: {result}")

        return result

    def run_session(self, execution_mode: str = "branch"):
        """Run the trading session based on the execution mode"""
        logger.info(f"Running session with execution mode: {execution_mode}")  # Ou
        if execution_mode == "branch":
            logger.info("Execution mode is 'branch', proceeding with branch trading.")
            self.execute_branch_trading()
        elif execution_mode == "parallel":
            logger.info("Execution mode is 'parallel', proceeding with parallel trading.")
            self.execute_parallel_trading()
        else:
            logger.error(f"Invalid execution mode: {execution_mode}")


if __name__ == "__main__":
    session = TradingSession(TRADING_CONFIG)
    execution_mode=TRADING_CONFIG.get("execution_mode")
    session.run_session(execution_mode=execution_mode)
