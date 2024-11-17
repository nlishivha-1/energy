from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from data_aquisition.da_config import get_db_connection
import pandas as pd
import streamlit as st


def create_temp_table():
    conn = get_db_connection()
    date_formatted = datetime.now().strftime("%d_%m_%y")
    table_name = f"temp_data_table_{date_formatted}"
    try:
        query = text(f"SELECT to_regclass('{table_name}');")
        result = conn.execute(query)
        if result.scalar() is None:
            conn.execute(
                text(
                    f"""CREATE TABLE {table_name} (
                    "Process_ID" VARCHAR(50),
                    "ID" INTEGER,
                    "Timestamp" TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    "Voltage" NUMERIC(6,2),
                    "Current" NUMERIC(6,2),
                    "Power" NUMERIC(8,2),
                    "Energy" NUMERIC(8,3),
                    "Frequency" NUMERIC(5,2),
                    "PF" NUMERIC(3,2)
                );"""
                )
            )
            print(f"Table {table_name} created successfully.")
            conn.commit()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def append_to_temp_table(data):
    conn = get_db_connection()
    date_formatted = datetime.now().strftime("%d_%m_%y")
    table_name = f"temp_data_table_{date_formatted}"
    try:
        query = text(
            f"""INSERT INTO {table_name} ("Process_ID", "ID", "Timestamp", "Voltage", 
                        "Current", "Power", "Energy", "Frequency", "PF") 
                        VALUES (:Process_ID, :ID, :Timestamp, :Voltage, :Current, :Power, 
                        :Energy, :Frequency, :PF);"""
        )
        conn.execute(query, data)
        conn.commit()
    except SQLAlchemyError as e:
        print(f"Database insert error: {e}")
    finally:
        conn.close()


# @st.cache_data
def load_historical_data():
    """Load historical data from the database and format it."""
    conn = get_db_connection()
    query = "SELECT * FROM historical_timeseries"
    df = pd.read_sql(query, conn)
    conn.close()

    df["Station"] = df["Process_ID"]  # Rename for consistency
    return df


def load_real_time_data():
    """Load real-time data for a specific station from the temporary data table."""
    conn = get_db_connection()
    date_formatted = datetime.now().strftime("%d_%m_%y")

    if conn:
        try:
            query = text(
                f"""
                SELECT * FROM temp_data_table_{date_formatted}
                ORDER BY "Timestamp" DESC
                LIMIT 120;
            """
            )
            real_time_df = pd.read_sql(query, conn)

            return real_time_df
        except SQLAlchemyError as db_error:
            print(f"Database error occurred while loading real-time data: {db_error}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            conn.close()  # Ensure the connection is closed after the operation
    else:
        print("Database connection failed.")
        return None


if __name__ == "__main__":
    create_temp_table()
