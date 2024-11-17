from db_operations import create_temp_table
from data_acquisition import read_serial_data

if __name__ == "__main__":
    create_temp_table()  # Ensures the table is created at startup
    read_serial_data(mock=True)  # Set mock=False for real serial data
