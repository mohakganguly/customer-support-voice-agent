import sqlite3
from pathlib import Path


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# SQLite database
DATABASE_PATH = DATA_DIR / "support.db"


def get_connection() -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    # Return rows that behave like dictionaries
    connection.row_factory = sqlite3.Row

    # Enforce foreign-key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection