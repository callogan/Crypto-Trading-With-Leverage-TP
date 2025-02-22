import logging
from typing import Dict, List


# Logging configuration
LOGGING_CONFIG: Dict = {
    "enabled": True,  # Enable/disable logging
    "level": logging.INFO,  # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": '%(asctime)s - %(levelname)s - %(message)s',
    "to_file": True,  # Enable/disable logging to file
    "console_output": True,  # Enable/disable console output
}

# Setup logging based on configuration
if LOGGING_CONFIG["enabled"]:
    handlers = []
    
    if LOGGING_CONFIG["console_output"]:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG["format"]))
        handlers.append(console_handler)
    
    if LOGGING_CONFIG["to_file"]:
        # Session-specific log handler
        session_handler = logging.FileHandler(LOGGING_CONFIG["log_file"])
        session_handler.setFormatter(logging.Formatter(LOGGING_CONFIG["format"]))
        handlers.append(session_handler)
        
        # General log handler (if enabled)
        if LOGGING_CONFIG["general_log"]["enabled"]:
            general_handler = logging.FileHandler(LOGGING_CONFIG["general_log"]["file"])
            general_handler.setFormatter(logging.Formatter(LOGGING_CONFIG["format"]))
            handlers.append(general_handler)
    
    logging.basicConfig(
        level=LOGGING_CONFIG["level"],
        format=LOGGING_CONFIG["format"],
        handlers=handlers
    )

logger = logging.getLogger('trading_bot')
# Disable logging if not enabled in config
if not LOGGING_CONFIG["enabled"]:
    logger.disabled = True

# Trading configuration
TRADING_CONFIG: Dict = {
    # File paths
    "keys_file": "wallet_keys.txt",
    "proxy_file": "proxies.txt",
    
    # Proxy settings
    "proxy_type": "regular",  # Options: "regular" or "mobile"
    
    # Execution settings
    "execution_mode": "branch",  # Options: "branch" or "parallel"
    "enable_shuffling": True,
    
    # Thread and branch settings
    "thread_count": 10,
    "launch_delay": (0, 3600),  # Delay range in seconds
    "branch_wallet_range": (2, 5),  # Min and max wallets per branch
    "max_parallel_branches": 5,
    
    # Trading parameters
    "trading_assets": ["BTC", "ETH", "SOL"],  # List of assets to trade
    "position_direction": "random",  # Options: "random", "long", "short"
    "volume_percentage_range": (10, 50),  # Min and max trade size
    
    # Additional trading settings
    "max_retries": 3,  # Maximum retry attempts for failed transactions
    "retry_delay": 5,  # Delay between retries in seconds
    "gas_limit": 300000,  # Maximum gas limit for transactions
    "slippage_tolerance": 0.5,  # Maximum allowed slippage in percentage
}

# User agents for transaction manager
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36",
]
