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
                    proxy_data, refresh_link = line.strip().split('|')
                    ip_port, auth = proxy_data.split("@")
                    proxies.append({
                        "ip_port": ip_port,
                        "auth": auth,
                        "refresh_link": refresh_link
                    })
                else:  # Regular proxy
                    ip_port, auth = line.strip().split('@')
                    proxies.append({
                        "ip_port": ip_port,
                        "auth": auth
                    })
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
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36"
        ]

    def get_random_user_agent(self) -> str:
        user_agent = random.choice(self.user_agents)
        return user_agent

    def _generate_signature(self, private_key: str, message: str) -> str:
        key = bytes.fromhex(private_key.replace("0x", ""))
        message_bytes = message.encode("utf-8")
        signature = hmac.new(key, message_bytes, hashlib.sha256).digest()
        return b64encode(signature).decode("utf-8")

    def execute_trade(self, wallet_key: str, asset: str, direction: str,
                      size: float, proxy: Dict) -> Dict[str, Any]:
        try:
            # Generate transaction ID
            tx_id = f"tx_{int(time.time())}_{random.randint(1000, 9999)}"

            # Simulate transaction validation
            if size > 10000:
                return {
                    "status": "failed",
                    "error": "Insufficient balance",
                    "timestamp": datetime.now().isoformat(),
                    "tx_id": tx_id
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
                    "wallet": wallet_key[:10] + "..."
                }
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
