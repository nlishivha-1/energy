import serial
import random
from datetime import datetime
from db_operations import append_to_temp_table
from data_aquisition.file_operations import append_to_csv
from data_aquisition.da_config import SERIAL_PORT, BAUD_RATE


def read_serial_data(mock=False):
    id_counter = 1
    while True:
        try:
            data = (
                generate_mock_data(id_counter) if mock else get_serial_data(id_counter)
            )
            append_to_csv(data)
            append_to_temp_table(data)
            id_counter += 1
        except Exception as e:
            print(f"Data acquisition error: {e}")


def get_serial_data(id_counter):
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        raw_data = ser.readline().decode("utf-8").strip()
        components = raw_data.split(",")
        if len(components) == 7:
            return format_data(id_counter, components)


def generate_mock_data(id_counter):
    return format_data(
        id_counter,
        [
            "station01",
            round(random.uniform(220, 230), 2),
            round(random.uniform(0.01, 0.05), 2),
            round(random.uniform(0, 5), 2),
            round(random.uniform(0, 1), 3),
            round(random.uniform(49.8, 50.2), 2),
            round(random.uniform(0, 1), 2),
        ],
    )


def format_data(id_counter, components):
    return {
        "Process_ID": "station01",
        "ID": id_counter,
        "Timestamp": datetime.now(),
        "Voltage": float(components[1]),
        "Current": float(components[2]),
        "Power": float(components[3]),
        "Energy": float(components[4]),
        "Frequency": float(components[5]),
        "PF": float(components[6]),
    }
