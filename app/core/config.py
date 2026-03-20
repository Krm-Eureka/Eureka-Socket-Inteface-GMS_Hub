import os
from dotenv import load_dotenv

load_dotenv(override=False)


class Settings:
    # Server (SERVER)
    BFF_HOST: str = os.getenv("BFF_HOST", "0.0.0.0")
    BFF_PORT: int = int(os.getenv("BFF_PORT", "9000"))
    BFF_RELOAD: bool = os.getenv("BFF_RELOAD", "false").lower() == "true"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # GMS Legacy Socket (SERVICE)
    GMS_IP: str = os.getenv("GMS_IP", "10.80.227.230")
    GMS_PORT: int = int(os.getenv("GMS_PORT", "24245"))
    GMS_CLIENT_CODE: str = os.getenv("GMS_CLIENT_CODE", "EA")
    GMS_CHANNEL_ID: str = os.getenv("GMS_CHANNEL_ID", "11111")
    GMS_HTTP_URL: str = os.getenv("GMS_HTTP_URL", "http://10.80.227.230:24249")

    # Mock Mode
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    # Polling Layers
    QUERY_INTERVAL_FAST: float = float(os.getenv("QUERY_INTERVAL_FAST", "1"))
    QUERY_INTERVAL_SLOW: float = float(os.getenv("QUERY_INTERVAL_SLOW", "30.0"))

    # Reconnection Backoff
    GMS_RECONNECT_INITIAL_DELAY: int = int(
        os.getenv("GMS_RECONNECT_INITIAL_DELAY", "5")
    )
    GMS_RECONNECT_MAX_DELAY: int = int(os.getenv("GMS_RECONNECT_MAX_DELAY", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MySQL Database (NEW)
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    # Security (NEW)
    GMS_SERVER_USER: str = os.getenv("GMS_SERVER_USER", "")
    GMS_SERVER_PASSWORD: str = os.getenv("GMS_SERVER_PASSWORD", "")


settings = Settings()
