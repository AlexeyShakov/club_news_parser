import asyncio

from db.db_connection import async_session_maker
from db.models import Error
from utils.enums import StepNameChoice
from src.config import console_logger


async def fill_errors():
    errors = [Error(step=el.name) for el in StepNameChoice]
    async with async_session_maker() as session:
        session.add_all(errors)
        await session.commit()
        console_logger.info("Ошибки успешно созданы")


if __name__ == '__main__':
    asyncio.run(fill_errors())
