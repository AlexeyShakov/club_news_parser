import aiohttp

from src.config import OVER_HTTP, OVER_QUEUE, OVER_GRPC, TRANSLATION_URL, console_logger, GRPC_TRANSLATION_PORT
from src.custom_exceptions import SenderNotFound
from src.db.models import Post
from src.config import logger
from src.utils.actions import update_db_elements_with_error
import grpc
from grpc_translations import translation_pb2, translation_pb2_grpc


async def send_to_translation_micro(news: list[Post]) -> None:
    if OVER_HTTP:
        return await send_by_http(news)
    if OVER_QUEUE:
        return
    if OVER_GRPC:
        return await send_over_grpc(news)
    raise SenderNotFound()


async def send_by_http(news: list[Post]) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            posts_for_translation = [post.to_translation_service() for post in news]
            async with session.post(TRANSLATION_URL, json=posts_for_translation) as resp:
                if resp.status != 204:
                    await update_db_elements_with_error(news)
                    return
                console_logger.exception("Новости успешно отправлены для перевода")
        except aiohttp.ClientConnectorError:
            logger.exception("Микросервис переводов недоступен")
            console_logger.exception("Микросервис переводов недоступен")
            # Соединяем ошибку со всеми новостями
            await update_db_elements_with_error(news)
        except Exception:
            logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
            console_logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
            await update_db_elements_with_error(news)


async def send_over_grpc(news: list[Post]) -> None:
    data_to_send = [
        translation_pb2.OneNews(id={"id": str(post.id)}, link={"link": post.link}, title={"title": post.title},
                                short_description={"short_description": post.short_description}) for post in news]
    channel = grpc.aio.insecure_channel(f"localhost:{GRPC_TRANSLATION_PORT}")
    stub = translation_pb2_grpc.NewsTranslatorStub(channel)
    try:
        await stub.GetNews(translation_pb2.News(
            news=data_to_send
        )
        )
        console_logger.exception("Новости успешно отправлены для перевода")
    except grpc.aio.AioRpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            logger.exception("Ошибка в валидации данных на сервисе переводов")
            console_logger.exception("Ошибка в валидации данных на сервисе переводов")
        elif rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
            logger.exception("Сервис переводов недоступен")
            console_logger.exception("Сервис переводов недоступен")
        else:
            logger.exception("Неизвестная ошибка на сервисе переводов")
            console_logger.exception("Неизвестная ошибка на сервисе переводов")
        await update_db_elements_with_error(news)
    except Exception:
        logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
        console_logger.exception("Неизвестная ошибка при попытки отправить данные на сервис переводов")
        await update_db_elements_with_error(news)
    finally:
        await channel.close()
