import os
import pandas as pd
import pytest
from datetime import datetime
from data_aquisition.da_config import STATION
from data_aquisition.file_operations import append_to_csv


@pytest.fixture
def sample_data():
    return {
        "Process_ID": STATION,
        "ID": 1,
        "Timestamp": datetime.now(),
        "Voltage": 220.0,
        "Current": 0.02,
        "Power": 1.2,
        "Energy": 0.003,
        "Frequency": 50.0,
        "PF": 0.99,
    }


def test_append_to_csv(sample_data):
    # Check that the file has the correct name format
    date_str = datetime.now().strftime("%d_%m_%y")
    expected_filename = f"{STATION}_{date_str}_temp.csv"

    # Run the append function
    append_to_csv(sample_data)

    # Check if the file exists
    assert os.path.exists(
        expected_filename
    ), f"File {expected_filename} does not exist."

    # Check that data is correctly appended
    df = pd.read_csv(expected_filename)
    assert df.shape[0] > 0, "No data in CSV file."

    # Cleanup the file after testing
    os.remove(expected_filename)
