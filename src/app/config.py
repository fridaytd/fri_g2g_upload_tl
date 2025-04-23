import os
from dotenv import load_dotenv


from pydantic import BaseModel


class Config(BaseModel):
    # Logger
    LOG_NAME: str
    LOG_LEVEL: str
    IS_LOG_FILE: str
    LOG_FILE_NAME: str

    # Keys
    KEYS_PATH: str

    # Sheets
    SPREADSHEET_KEY: str
    SHEET_NAME: str

    # G2G KEYS
    G2G_ACCOUNT_ID: str
    G2G_API_KEY: str
    G2G_SECRET_KEY: str

    # Relax time each round in second
    RELAX_TIME_EACH_ROUND: int

    @staticmethod
    def from_env() -> "Config":
        load_dotenv("setting.env")
        return Config.model_validate({k: v for k, v in os.environ.items()})


config = Config.from_env()
