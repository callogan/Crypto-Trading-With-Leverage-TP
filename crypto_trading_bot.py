import hashlib
import hmac
import os
import random
import requests
import time

from base64 import b64encode
from datetime import datetime
from typing import List, Dict, Any, Tuple


class WalletManager:
    def __init__(self, keys_file: str = "wallet_keys.txt"):
        self.keys_file = keys_file
        self.wallets = self._load_wallets()

    def _load_wallets(self) -> List[str]:
        if not os.path.exists(self.keys_file):
            return []

        with open(self.keys_file, "r") as f:
            wallets = [line.strip() for line in f if line.strip()]
            return wallets

    def add_wallet(self, private_key: str):
        with open(self.keys_file, "a") as f:
            f.write(f"{private_key}\n")
        self.wallets.append(private_key)

    def get_next_wallet(self, index: int) -> str:
        if 0 <= index < len(self.wallets):
            return self.wallets[index]
        return None


class ProxyManager:
    def __init__(self, proxy_file: str, proxy_type: str = "regular"):
        self.proxy_file = proxy_file
        self.proxy_type = proxy_type
        self.proxies = self._load_proxies()

    def _load_proxies(self) -> List[Dict]:
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
                    proxies.append({"ip_port": ip_port, "auth": auth})
            return proxies

    def get_proxy(self, account_id: int) -> Dict:
        proxy = self.proxies[account_id % len(self.proxies)]
        if self.proxy_type == "mobile" and "refresh_link" in proxy:
            requests.get(proxy["refresh_link"])
        return proxy


class TransactionManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
        ]

    def get_random_user_agent(self) -> str:
        user_agent = random.choice(self.user_agents)
        return user_agent

    def _generate_signature(self, private_key: str, message: str) -> str:
        key = bytes.fromhex(private_key.replace("0x", ""))
        message_bytes = message.encode("utf-8")
        signature = hmac.new(key, message_bytes, hashlib.sha256).digest()
        return b64encode(signature).decode("utf-8")

    def execute_trade(
        self, wallet_key: str, asset: str, direction: str, size: float, proxy: Dict
    ) -> Dict[str, Any]:
        try:
            # Generate transaction ID
            tx_id = f"tx_{int(time.time())}_{random.randint(1000, 9999)}"

            # Simulate transaction validation
            if size > 10000:
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

    def execute_branch_trading(self):
        branch_range = self.config.get("branch_wallet_range", (2, 5))
        max_branches = self.config.get("max_parallel_branches", 5)

        wallets = self.wallet_manager.wallets.copy()
        if self.config.get("enable_shuffling", True):
            random.shuffle(wallets)

        active_branches = 0
        while wallets and active_branches < max_branches:
            branch_size = random.randint(*branch_range)
            if len(wallets) < branch_size:
                break

            branch_wallets = wallets[:branch_size]
            wallets = wallets[branch_size:]

            # Split into long and short positions
            long_count = random.randint(1, branch_size - 1)
            short_count = branch_size - long_count

            self._process_branch(branch_wallets, long_count, short_count)
            active_branches += 1

    def execute_parallel_trading(self):
        thread_count = self.config.get("thread_count", 10)
        delay_range = self.config.get("launch_delay", (0, 20))

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
        if not self.wallet_manager.wallets:  # Additional check prior to the trade
            return  # Exit if no available wallets

        wallet_index = self.wallet_manager.wallets.index(wallet_key)
        wallet = self.wallet_manager.get_next_wallet(wallet_index)
        if not wallet:
            return

        proxy = self.proxy_manager.get_proxy(
            self.wallet_manager.wallets.index(wallet_key)
        )

        # Execute trade based on configuration
        asset = random.choice(self.config.get("trading_assets", ["BTC", "ETH", "SOL"]))
        direction = self._get_trade_direction()
        size = self._get_trade_size()

        result = self.transaction_manager.execute_trade(
            wallet_key, asset, direction, size, proxy
        )

    def _process_branch(self, wallets: List[str], long_count: int, short_count: int):
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
        direction_config = self.config.get("position_direction", "random")
        if direction_config == "random":
            return random.choice(["long", "short"])
        return direction_config

    def _get_trade_size(self) -> float:
        volume_range = self.config.get("volume_percentage_range", (10, 50))
        return random.uniform(*volume_range)

    def _process_wallet_with_size(
        self, wallet: str, direction: str, size: float
    ) -> Dict[str, Any]:
        proxy = self.proxy_manager.get_proxy(self.wallet_manager.wallets.index(wallet))
        asset = random.choice(self.config.get("trading_assets", ["BTC", "ETH", "SOL"]))

        result = self.transaction_manager.execute_trade(
            wallet, asset, direction, size, proxy
        )

        return result

    def run_session(self, execution_mode: str = "branch"):
        if execution_mode == "branch":
            self.execute_branch_trading()
        elif execution_mode == "parallel":
            self.execute_parallel_trading()


if __name__ == "__main__":
    # Example configuration
    config = {
        "keys_file": "wallet_keys.txt",
        "proxy_file": "proxies.txt",
        "proxy_type": "regular",
        "enable_logs": True,
        "enable_shuffling": True,
        "thread_count": 10,
        "launch_delay": (0, 20),
        "branch_wallet_range": (2, 5),
        "max_parallel_branches": 5,
        "trading_assets": ["BTC", "ETH", "SOL"],
        "position_direction": "random",
        "volume_percentage_range": (10, 50),
    }

    # Initialize and run trading session
    session = TradingSession(config)

    session.run_session(execution_mode="branch")  # or "parallel"
