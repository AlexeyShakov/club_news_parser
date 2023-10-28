import aiohttp
import asyncio
from src.html_hanlder import HtmlHandler
from bs4 import BeautifulSoup
from src.config import logger, console_logger, GETTING_NEWS_INTERVAL, OVER_GRPC, OVER_HTTP
from threading import Thread
from src.utils.delete_old_news import delete_outdated_news
from src.db.error_filler import fill_errors

from src.utils.resend_error_news import handle_resending


FOOTBALL_CLUBS = {
    "MU": "https://www.skysports.com/manchester-united",
    "MC": "https://www.skysports.com/manchester-city",
    "Chelsea": "https://www.skysports.com/chelsea",
    "Arsenal": "https://www.skysports.com/arsenal",
    "Liverpool": "https://www.skysports.com/liverpool"
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
    await fill_errors()
    console_logger.info("Приложение запустилось")
    while True:
        await form_tasks()
        await asyncio.sleep(GETTING_NEWS_INTERVAL)


def start_background_tasks():
    # Если микросервисы общаются через RabbitMQ, то нам не нужно самим отправлять неотправленные новости,
    # т.к. RabbitMQ сделаем это за нас
    if OVER_HTTP or OVER_GRPC:
        thread_2 = Thread(target=handle_resending)
        thread_2.start()
    thread_1 = Thread(target=delete_outdated_news)
    thread_1.start()


if __name__ == '__main__':
    start_background_tasks()
    asyncio.run(start_app())
