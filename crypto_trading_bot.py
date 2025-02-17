import os
from typing import List, Dict, Any, Tuple

import requests


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
