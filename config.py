from sqlalchemy import create_engine
from env import *


class DatabaseConfig:
    def __init__(self):
        self.db_user = DB_USER
        self.db_password = DB_PASSWORD
        self.db_host = DB_HOST
        self.db_name = DB_NAME

    def create_engine(self):
        return create_engine(
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
        )


MODEL = "model/random_forest_energy_model_20241113_203659.pkl"
