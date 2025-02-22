import logging

from crypto_trading_bot import TradingSession
from config import logger, TRADING_CONFIG, LOGGING_CONFIG


def main():
    """
    Main function, which settings up logging,
    configures trade session, executes trading based on configuration
    """
    try:
        # Initialize trading session with configuration
        session = TradingSession(TRADING_CONFIG)
        
        # Run trading session with configured execution mode
        execution_mode = TRADING_CONFIG.get("execution_mode", "branch")
        
        if LOGGING_CONFIG["enabled"]:
            logger.info(f"Starting trading session with mode: {execution_mode}")
        
        session.run_session(execution_mode=execution_mode)
        
    except Exception as e:
        if LOGGING_CONFIG["enabled"]:
            logger.error(f"Trading session failed: {str(e)}")
        raise
    finally:
        if LOGGING_CONFIG["enabled"]:
            logger.info("Trading session completed")


if __name__ == "__main__":
    main()
