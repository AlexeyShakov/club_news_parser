from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

# Базовый класс для SQLAlchemy моделей(таблиц)
Base = declarative_base()

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_SYNC = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


sync_engine = create_engine(DATABASE_URL_SYNC)
sync_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
