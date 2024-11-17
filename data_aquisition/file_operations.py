import os
import pandas as pd
from data_aquisition.da_config import TEMP_DATA_FILE


def append_to_csv(data):
    """Append new data to the temporary CSV file."""
    df = pd.DataFrame([data])
    df.to_csv(
        TEMP_DATA_FILE, mode="a", header=not os.path.exists(TEMP_DATA_FILE), index=False
    )
