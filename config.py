import os

DB_NAME = "binance.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)
DB_CONNECTION_STRING = f"sqlite:///{DB_PATH}"

# Generation settings
NUM_USERS = 5000
NUM_EVENTS = 500000
START_DATE = "2023-01-01"
END_DATE = "2023-06-30"

TOKENS = ["BTC", "ETH", "SOL", "PEPE", "ARB", "OP", "DOGE", "XRP", "ADA", "AVAX"]
