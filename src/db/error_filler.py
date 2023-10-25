import asyncio

from sqlalchemy import select

from src.db.db_connection import async_session_maker
from src.db.models import Error
from src.utils.enums import StepNameChoice
from src.config import console_logger


async def fill_errors():
    async with async_session_maker() as session:
        query = select(Error)
        result = await session.execute(query)
        error = result.scalars().first()
        if not error:
            errors = [Error(step=el.name) for el in StepNameChoice]
            session.add_all(errors)
            await session.commit()
            console_logger.info("Ошибки успешно созданы")
            return
        console_logger.info("Ошибки уже созданы")


if __name__ == '__main__':
    asyncio.run(fill_errors())
