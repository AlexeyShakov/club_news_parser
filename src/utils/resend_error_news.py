import time
from typing import Sequence

from sqlalchemy import select, or_

from src.config import TELEGRAM_URL, console_logger, logger, TRANSLATION_URL, RESENDING_INTERVAL
from src.db.db_connection import sync_session_maker
from src.db.models import Post, Error
from src.utils.enums import StepNameChoice
import requests


def handle_resending():
    while True:
        console_logger.info("Пытаемся послать неотправленные новости")
        resender = NewsResender()
        resender.resend_news()
        time.sleep(RESENDING_INTERVAL)


class NewsResender:
    TRANSLATION_NEWS = []
    TELEGRAM_NEWS = []

    def resend_news(self) -> None:
        posts = self._get_posts()
        if not posts:
            return
        self._filter_news(posts)
        self._send_news(TRANSLATION_URL, self.TRANSLATION_NEWS)
        self._send_news(TELEGRAM_URL, self.TELEGRAM_NEWS)

    def _get_posts(self) -> Sequence[Post]:
        with sync_session_maker() as session:
            query = select(Post).join(Post.error).where(
                or_(Error.step == StepNameChoice.SENDING_TO_TRANSLATION.name,
                    Error.step == StepNameChoice.SENDING_TO_TELEGRAM.name))
            result = session.execute(query)
            return result.scalars().all()

    def _filter_news(self, posts: Sequence[Post]) -> None:
        for post in posts:
            if post.error.step.name == StepNameChoice.SENDING_TO_TRANSLATION.name:
                self.TRANSLATION_NEWS.append(post.to_translation_service())
            else:
                self.TELEGRAM_NEWS.append(post.to_telegram_service())

    def _send_news(self, url: str, news: list[dict]) -> None:
        try:
            response = requests.post(url=url, json=news)
            if response.status_code != 204:
                console_logger.info(f"Повторный запрос на {url} неудачный")
        except requests.exceptions.ConnectionError:
            logger.exception(f"{url} не отвечает при повторной попытке отправить новости")
            console_logger.info(
                f"{url} не отвечает при повторной попытке отправить новости"
            )
        except Exception:
            logger.exception(f"При повторной попытке отправить данные на {url} возникла неизвестная ошибка")
            console_logger.info(
                f"При повторной попытке отправить данные на {url} возникла неизвестная ошибка"
            )