from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

# Базовый класс для SQLAlchemy моделей(таблиц)
Base = declarative_base()