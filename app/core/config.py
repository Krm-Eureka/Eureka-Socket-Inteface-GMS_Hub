import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Server (SERVER)
    BFF_HOST: str = os.getenv("BFF_HOST", "0.0.0.0")
    BFF_PORT: int = int(os.getenv("BFF_PORT", "1244"))
    BFF_RELOAD: bool = os.getenv("BFF_RELOAD", "false").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # GMS Legacy Socket (SERVICE)
    GMS_IP: str = os.getenv("GMS_IP", "10.80.227.230")
    GMS_PORT: int = int(os.getenv("GMS_PORT", "24245"))
    GMS_CLIENT_CODE: str = os.getenv("GMS_CLIENT_CODE", "MEKTEC")
    GMS_CHANNEL_ID: str = os.getenv("GMS_CHANNEL_ID", "11111")

    # Mock Mode
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MySQL Database (NEW)
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "")


settings = Settings()
