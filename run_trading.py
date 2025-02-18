import logging

from crypto_trading_bot import TradingSession


def main():
    """
    Main function, which settings up logging,
    configures trade session, executes both branch
    and parallel trading
    """

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Trading configuration
    config = {
        "keys_file": "wallet_keys.txt",
        "proxy_file": "proxies.txt",
        "proxy_type": "regular",
        "enable_logs": True,
        "enable_shuffling": True,
        "thread_count": 2,  # Start with small number
        "launch_delay": (5, 10),  # Short delays
        "branch_wallet_range": (2, 3),
        "max_parallel_branches": 2,
        "trading_assets": ["BTC", "ETH", "SOL"],
        "position_direction": "random",
        "volume_percentage_range": (10, 50),
        "trades_per_wallet": 2,
    }

    # Initialize trading session
    session = TradingSession(config)

    try:

        # Executes branch trading
        logging.info("Starting branch trading ...")
        session.execute_branch_trading()
        logging.info("Branch trading completed")

        # Executes parallel trading
        logging.info("Starting parallel trading ...")
        session.execute_parallel_trading()
        logging.info("Parallel trading completed")

    except Exception as e:
        logging.error(f"Trading error: {str(e)}")

if __name__ == "__main__":
    main()
