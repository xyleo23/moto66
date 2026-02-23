"""Конфигурация бота. Загрузка переменных из .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env из корня проекта
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
SUPERADMIN_ID: int = int(os.getenv("SUPERADMIN_ID", "0"))

# База данных (SQLite по умолчанию)
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./moto66.db",
)

# ЮKassa / Telegram Payments (Provider Token от @BotFather)
PAYMENT_PROVIDER_TOKEN: str = os.getenv("PAYMENT_PROVIDER_TOKEN", "")

# Канал/чат для заявок на двойку
DOUBLE_REQUESTS_CHAT_ID: str = os.getenv("DOUBLE_REQUESTS_CHAT_ID", "")

# Требования для заявки на двойку (настраиваемые)
DOUBLE_MIN_EXPERIENCE: int = int(os.getenv("DOUBLE_MIN_EXPERIENCE", "3"))
DOUBLE_MIN_ENGINE_CAPACITY: int = int(os.getenv("DOUBLE_MIN_ENGINE_CAPACITY", "400"))
DOUBLE_FORBIDDEN_MOTO_TYPE: str = os.getenv("DOUBLE_FORBIDDEN_MOTO_TYPE", "спорт")

# Google Sheets: путь к JSON-ключу сервисного аккаунта
GOOGLE_CREDENTIALS_PATH: str = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    str(Path(__file__).resolve().parent / "google_credentials.json"),
)
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
