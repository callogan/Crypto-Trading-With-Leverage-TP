import os
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
