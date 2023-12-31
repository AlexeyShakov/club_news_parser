from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.datastructures import Post
from dataclasses import asdict

from src.db.db_connection import async_session_maker
from src.utils.enums import StepNameChoice
from src.db.models import Post as PostDB, Error
from src.config import console_logger


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
        from src.utils.send_to_translations_utils.senders import send_to_translation_micro
        await send_to_translation_micro(db_elements)


async def update_db_elements_with_error(news: list[PostDB]) -> None:
    async with async_session_maker() as session:
        query = select(Error).where(Error.step == StepNameChoice.SENDING_TO_TRANSLATION.name)
        result = await session.execute(query)
        error = result.scalars().first()

        modified_posts = []
        for post in news:
            post.error_id = error.id
            modified_posts.append(post)
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



