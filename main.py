import aiohttp
import asyncio
from html_hanlder import HtmlHandler
from bs4 import BeautifulSoup
from config import logger
"""
+ 1. Функция, которая будет проходится по всем футбольным командам и запускать функцию для стягивания материала.
+ 2. Функция, которая стягивает html страницу определенной футбольной команды.
+ 3. Сущность для парсинга html страницы и вытягиванию только нужных данных
    - т.к. есть три разных вида постов, то возможно придется для каждого поста сделать свой метод
    - возможно это будет класс, т.к. мы будем парсить информацию об одном клубе и в конечном итоге
        нам нужно хранить состояния - конечный итог обработки html. Конечный итог, это информация о всех статьях
4. Сохранение статей в базу
5. Посыл данных на другой микросервис
6. Переодическая задача для вызова функции по стягиванию информации
7. Переодическая задача по удалению устаревших данных из базы.
"""

FOOTBALL_CLUBS = {
    "MU": "https://www.skysports.com/manchester-united",
    "MC": "https://www.skysports.com/manchester-city"
}

async def get_club_info(url: str, club_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                await HtmlHandler(
                    BeautifulSoup(await response.text(), "lxml")
                ).process_html()
            else:
                logger.exception(f"Неудачная попытка при получении новостей клуба {club_name}. Код ошибки: {response.status}")


async def form_tasks() -> None:
    tasks = [asyncio.create_task(get_club_info(FOOTBALL_CLUBS[club_name], club_name)) for club_name in FOOTBALL_CLUBS]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(form_tasks())

