from crypto_trading_bot import TradingSession


def main():
    # Trading configuration
    config = {
        "keys_file": "wallet_keys.txt",
        "proxy_file": "proxies.txt",
        "proxy_type": "regular",
        "enable_logs": True,
        "enable_shuffling": True,
        "thread_count": 2,  # Start with small number for testing
        "launch_delay": (5, 10),  # Short delays for testing
        "branch_wallet_range": (2, 3),
        "max_parallel_branches": 2,
        "trading_assets": ["BTC", "ETH", "SOL"],
        "position_direction": "random",
        "volume_percentage_range": (10, 50),
        "trades_per_wallet": 2,
    }

    # Initialize trading session
    session = TradingSession(config)

    # Test parallel trading
    session.execute_parallel_trading()

    # Test branch trading
    session.execute_branch_trading()


if __name__ == "__main__":
    main()
