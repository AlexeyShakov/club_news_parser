from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datastructures import Post
from dataclasses import asdict

from db_connection import async_session_maker
from enums import StepNameChoice
from models import Post as PostDB
from models import Error
import aiohttp
from config import logger, console_logger


async def save_news_list_into_db(news: list[Post]) -> None:
    async with async_session_maker() as session:
        news = await exclude_existing_news(news, session)
        if not len(news):
            console_logger.info("Новых новостей нет")
            return
        db_elements = [PostDB(**asdict(element)) for element in news]
        session.add_all(db_elements)
        await session.commit()
    if news:
        await send_to_translation_micro(news)


async def update_db_elements_with_error(news: list[Post]) -> None:
    async with async_session_maker() as session:
        query = select(Error).where(Error.step == StepNameChoice.SENDING_TO_TRANSLATION.name)
        result = await session.execute(query)
        error = result.scalars().first()

        news_titles = [element.title for element in news]
        post_query = select(PostDB).where(PostDB.title.in_(news_titles))
        result = await session.execute(post_query)
        modified_posts = []
        for el in result.scalars().all():
            el.error_id = error.id
            modified_posts.append(el)
        session.add_all(modified_posts)
        await session.commit()


async def exclude_existing_news(news: list[Post], session: AsyncSession) -> list[Post]:
    news_titles = [element.title for element in news]
    # Находим те статьи, что уже есть в базе
    query = select(PostDB.title).where(PostDB.title.in_(news_titles))
    db_elements = await session.execute(query)
    # Внутри будет лежать [("something long",), ("something long again"), ...]
    result = db_elements.all()
    plain_result = [element[0] for element in result]
    if not plain_result:
        return news
    return [element for element in news if element.title not in plain_result]


async def send_to_translation_micro(news: list[Post]):
    async with aiohttp.ClientSession() as session:
        try:
            # Написать нормальный URL сервиса переводов TODO
            async with session.post('http://something_228.com', json=asdict(news[0])) as resp:
                pass
        except aiohttp.ClientConnectorError:
            logger.exception("Микросервис переводов недоступен")
            console_logger.exception("Микросервис переводов недоступен")
            # Соединяем ошибку со всеми новостями
            await update_db_elements_with_error(news)
        except Exception:
            logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
            console_logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
            await update_db_elements_with_error(news)
