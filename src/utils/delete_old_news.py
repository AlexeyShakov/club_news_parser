import time
from datetime import date, timedelta

from sqlalchemy import delete
from src.config import console_logger
from src.config import OUTDATING_INTERVAL, DELETING_OUTDATED_NEWS_INTERVAL
from src.db.db_connection import sync_session_maker
from src.db.models import Post


def delete_outdated_news():
    while True:
        console_logger.info("Удаляем устаревшие новости")
        # Получаем даты, которые старше сегодняшней на 3 дня
        with sync_session_maker() as session:
            stmt = delete(Post).where(Post.success_date <= (date.today() - timedelta(days=OUTDATING_INTERVAL)))
            session.execute(stmt)
            session.commit()
        time.sleep(DELETING_OUTDATED_NEWS_INTERVAL)
