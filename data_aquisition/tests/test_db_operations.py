import pytest
from data_aquisition.db_operations import create_temp_table, append_to_temp_table
from datetime import datetime


@pytest.fixture
def sample_data():
    return {
        "Process_ID": "station01",
        "ID": 1,
        "Timestamp": datetime.now(),
        "Voltage": 220.0,
        "Current": 0.02,
        "Power": 1.2,
        "Energy": 0.003,
        "Frequency": 50.0,
        "PF": 0.99,
    }


def test_create_temp_table():
    # Check if the table can be created
    try:
        create_temp_table()
        assert True
    except Exception as e:
        pytest.fail(f"Table creation failed: {e}")


def test_append_to_temp_table(sample_data):
    # Check if data can be appended without errors
    try:
        append_to_temp_table(sample_data)
        assert True
    except Exception as e:
        pytest.fail(f"Data append failed: {e}")
