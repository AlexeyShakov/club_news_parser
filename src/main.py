import aiohttp
import asyncio
from src.html_hanlder import HtmlHandler
from bs4 import BeautifulSoup
from src.config import logger
"""
6. Переодическая задача для вызова функции по стягиванию информации
7. Переодическая задача по удалению устаревших данных из базы.
"""

FOOTBALL_CLUBS = {
    "MU": "https://www.skysports.com/manchester-united",
    "MC": "https://www.skysports.com/manchester-city"
}

async def get_club_info(url: str, club_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    await HtmlHandler(
                        BeautifulSoup(await response.text(), "lxml")
                    ).process_html()
                else:
                    logger.exception(f"Неудачная попытка при получении новостей клуба {club_name}. Код ошибки: {response.status}")
        except aiohttp.ClientConnectorError:
            logger.exception(f"Неудалось получить информацию о клубе {club_name}")
        except Exception:
            logger.exception(f"Неизвестная ошибка при попытке получить информацию о клубе {club_name}")


async def form_tasks() -> None:
    tasks = [asyncio.create_task(get_club_info(FOOTBALL_CLUBS[club_name], club_name)) for club_name in FOOTBALL_CLUBS]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(form_tasks())

