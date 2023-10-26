import time
from typing import Sequence

import grpc
from grpc_service import telegram_pb2_grpc, telegram_pb2, translation_pb2, translation_pb2_grpc
from sqlalchemy import select, or_

from src.config import TELEGRAM_URL, console_logger, logger, TRANSLATION_URL, RESENDING_INTERVAL, OVER_GRPC, OVER_HTTP, \
    OVER_QUEUE, GRPC_TRANSLATION_PORT, GRPC_TELEGRAM_PORT, TRANSLATION_CONTAINER, TELEGRAM_CONTAINER
from src.db.db_connection import sync_session_maker
from src.db.models import Post, Error
from src.utils.enums import StepNameChoice
import requests
from src.custom_exceptions import SenderNotFound


def handle_resending():
    while True:
        console_logger.info("Пытаемся послать неотправленные новости")
        resender = NewsResender()
        resender.resend_news()
        time.sleep(RESENDING_INTERVAL)


class NewsResender:
    def __init__(self):
        self.TRANSLATION_NEWS = []
        self.TELEGRAM_NEWS = []

    def resend_news(self) -> None:
        posts = self._get_posts()
        if not posts:
            return
        self._filter_news(posts)
        self._send_news()

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

    def _send_news(self) -> None:
        if OVER_HTTP:
            if self.TRANSLATION_NEWS:
                self._send_news_by_http(TRANSLATION_URL, self.TRANSLATION_NEWS)
            if self.TELEGRAM_NEWS:
                self._send_news_by_http(TELEGRAM_URL, self.TELEGRAM_NEWS)
            return
        if OVER_GRPC:
            if self.TRANSLATION_NEWS:
                self.send_over_grpc_to_translation(self.TRANSLATION_NEWS)
            if self.TELEGRAM_NEWS:
                self.send_over_grpc_to_telegram(self.TELEGRAM_NEWS)
            return
        if OVER_QUEUE:
            return
        raise SenderNotFound()

    def send_over_grpc_to_telegram(self, news: list[dict]) -> None:
        channel = grpc.aio.insecure_channel(f"{TELEGRAM_CONTAINER}:{GRPC_TELEGRAM_PORT}")
        stub = telegram_pb2_grpc.NewsTelegramStub(channel)
        data_to_send = [
            telegram_pb2.OneTranslatedNews(id={"id": post["id"]}, link={"link": post["link"]},
                                           translated_title={"translated_title": post["translated_title"]},
                                           translated_short_description={
                                               "translated_short_description": post["translated_short_description"]})
            for post in news]
        try:
            stub.GetNews(telegram_pb2.TranslatedNews(
                news=data_to_send
            ))
            console_logger.info("Данные успешно переданы на микросервис управлением телеграмма")
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                logger.exception("Сервис телеграма недоступен при повторной отправки новостей")
                console_logger.exception("Сервис телеграма недоступен повторной отправки новостей")
            else:
                logger.exception("Неизвестная ошибка на сервисе телеграмма  при повторной отправки новостей")
                console_logger.exception("Неизвестная ошибка на сервисе телеграмма при повторной отправки новостей")
        finally:
            channel.close()

    def send_over_grpc_to_translation(self, news: list[dict]) -> None:
        data_to_send = [
            translation_pb2.OneNews(id={"id": post["id"]}, link={"link": post["link"]},
                                    title={"title": post["title"]},
                                    short_description={"short_description": post["short_description"]}) for post in
            news]
        channel = grpc.insecure_channel(f"{TRANSLATION_CONTAINER}:{GRPC_TRANSLATION_PORT}")
        stub = translation_pb2_grpc.NewsTranslatorStub(channel)
        try:
            stub.GetNews(translation_pb2.News(
                news=data_to_send))
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                logger.exception("Сервис переводов недоступен при повторной отправке новостей")
                console_logger.exception("Сервис переводов недоступен повторной отправке новостей")
            else:
                logger.exception(f"Неизвестная ошибка на сервисе переводов: {rpc_error}")
                console_logger.exception("Неизвестная ошибка на сервисе переводов")
        finally:
            channel.close()

    def _send_news_by_http(self, url: str, news: list[dict]) -> None:
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
