import os
from datetime import datetime
from config import DatabaseConfig
from sqlalchemy.exc import SQLAlchemyError

# Serial Port Configuration
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = int(os.getenv("BAUD_RATE", 9600))

# Database Configuration
# Create the database engine
engine = DatabaseConfig().create_engine()

# Global persistent connection
persistent_connection = None


def get_db_connection():
    """Get a persistent database connection, reconnecting if necessary."""
    global persistent_connection
    print("Getting a database connection")
    try:
        # Check if the connection is inactive or closed
        if persistent_connection is None or persistent_connection.closed:
            print("Establishing a new connection")
            persistent_connection = engine.connect()
            print("Database connection established or reconnected successfully.")
        else:
            print("Using existing connection")
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")
        persistent_connection = None
    return persistent_connection


# Station Name and Data File Path
STATION = os.getenv("STATION", "station01")
TEMP_DATA_FILE = os.getenv(
    "TEMP_DATA_FILE", f"{STATION}_{datetime.now().strftime('%d_%m_%y')}_temp.csv"
)
