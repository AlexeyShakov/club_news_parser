import aiohttp
import asyncio
from src.html_hanlder import HtmlHandler
from bs4 import BeautifulSoup
from src.config import logger, console_logger, GETTING_NEWS_INTERVAL

"""
6. Переодическая задача для вызова функции по стягиванию информации
7. Переодическая задача по удалению устаревших данных из базы.
"""

FOOTBALL_CLUBS = {
    "MU": "https://www.skysports.com/manchester-united",
    # "MC": "https://www.skysports.com/manchester-city"
}


async def get_club_info(url: str, club_name: str) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.exception(
                        f"Неудачная попытка при получении новостей клуба {club_name}. Код ошибки: {response.status}")
                    console_logger.exception(
                        f"Неудачная попытка при получении новостей клуба {club_name}. Код ошибки: {response.status}")
                    return
                console_logger.info(f"Новости для команды {club_name} успешно получены")
                await HtmlHandler(
                    BeautifulSoup(await response.text(), "lxml")
                ).process_html()
        except aiohttp.ClientConnectorError:
            logger.exception(f"Неудалось получить информацию о клубе {club_name}")
            console_logger.exception(f"Неудалось получить информацию о клубе {club_name}")
        except Exception:
            logger.exception(f"Неизвестная ошибка при попытке получить информацию о клубе {club_name}")
            console_logger.exception(f"Неизвестная ошибка при попытке получить информацию о клубе {club_name}")


async def form_tasks() -> None:
    tasks = [asyncio.create_task(get_club_info(FOOTBALL_CLUBS[club_name], club_name)) for club_name in FOOTBALL_CLUBS]
    await asyncio.gather(*tasks)


async def start_app():
    while True:
        print("Перед запуском команды")
        await form_tasks()
        print("Запустил таски щас буду спать")
        await asyncio.sleep(GETTING_NEWS_INTERVAL)

if __name__ == '__main__':
    # asyncio.run(start_app())
    asyncio.run(form_tasks())