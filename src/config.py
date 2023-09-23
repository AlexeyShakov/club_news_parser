from dotenv import load_dotenv
import os
import logging


load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT")


logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(os.path.join(os.getcwd(), "logs/logs.log"), encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

