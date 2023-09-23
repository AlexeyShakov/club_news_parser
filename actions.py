from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datastructures import Post
from dataclasses import asdict

from db_connection import async_session_maker
from models import Post as PostDB


async def save_news_list_into_db(news: list[Post]) -> None:
    async with async_session_maker() as session:
        news = await exclude_existing_news(news, session)
        if not len(news):
            return
        db_elements = [PostDB(**asdict(element)) for element in news]
        session.add_all(db_elements)
        await session.commit()

async def save_one_news_into_db(news: Post) -> None:
    # Здесь нужно будет добавить параметр в функции, которая будет отвечать за
    async with async_session_maker() as session:
        session.add(PostDB(**asdict(news)))
        await session.commit()


async def exclude_existing_news(news: list[Post], session: AsyncSession) -> set[Post]:
    # Проверить на одной команде, что все отабатывает верно TODO
    news_titles = {element.title: element for element in news}
    # Находим те статьи, что уже есть в базе
    query = select(PostDB.title).where(PostDB.title.in_(news_titles))
    db_elements = await session.execute(query)
    # Внутри будет лежать [("something long",), ("something long again"), ...]
    result = db_elements.all()
    result_as_set = set(element[0] for element in result)
    return set(news_titles) - result_as_set


async def send_to_translation_micro(news: list[Post]):
    pass