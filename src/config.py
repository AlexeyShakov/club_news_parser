from pathlib import Path

from dotenv import load_dotenv
import os
import logging


load_dotenv()

BASE_DIR = Path(os.path.abspath(__file__)).parent.parent

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT")

TRANSLATION_URL = os.getenv("TRANSLATION_URL")
TELEGRAM_URL = os.getenv("TELEGRAM_URL")

OUTDATING_INTERVAL = 3


logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    file_handler = logging.FileHandler(os.path.join(BASE_DIR, "logs/logs.log"),
                                       encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

console_logger = logging.getLogger("console_logger")
console_logger.setLevel(logging.INFO)
if not console_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_logger.addHandler(console_handler)

# в секундах
GETTING_NEWS_INTERVAL = 60
