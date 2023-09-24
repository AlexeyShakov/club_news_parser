import asyncio

from bs4 import BeautifulSoup
from src.config import logger, console_logger
from src.datastructures import Post, PostTagInfo
from src.actions import save_news_list_into_db


class HtmlHandler:
    """
    Данный класс обрабатывает HTML-страницу с определенной футбольной командой. На странице есть 3 типа новости:
    * главная новость - связана с тегом, где  "class"="news-top-story__body"
    * две менее главные новости - связаны с тегом, где "class"="grid news-list-featured block"
    * другие новости(5 шт) - связаны с тегом, где "class"="news-list block"
    """

    def __init__(self, prepared_soup: BeautifulSoup):
        self.prepared_soup = prepared_soup
        self.prepared_data = []
        self.lock = asyncio.Lock()

    async def process_html(self):
        """
        Здесь создаем задачи для каждого типа постов на выходе должны заполнить self.prepared_data
        """
        featured_news = PostTagInfo(
            block_data=("div", {"class": "grid news-list-featured block"}),
            post_data=("div", {"class": "grid__col news-list-featured__item"}),
            link_and_title_data=("a", {"class": "news-list-featured__figure"}),
            short_description_data=("p", {"class": "news-list-featured__snippet"})

        )
        latest_news = PostTagInfo(
            block_data=("div", {"class": "news-list block"}),
            post_data=("div", {"class": "news-list__item"}),
            link_and_title_data=("a", {"class": "news-list__figure"}),
            short_description_data=("p", {"class": "news-list__snippet"})
        )
        main_news_task = asyncio.create_task(self.process_main_post())
        features_news_task = asyncio.create_task(self.process_other_posts(featured_news))
        latest_news_task = asyncio.create_task(self.process_other_posts(latest_news))
        await asyncio.gather(main_news_task, features_news_task, latest_news_task)
        if not self.prepared_data:
            logger.exception("При обработке html-страниц получили 0 новостей")
            console_logger.exception("При обработке html-страниц получили 0 новостей")
            return
        logger.info("Новости успешно сгенерированы")
        console_logger.exception("Новости успешно сгенерированы")
        await save_news_list_into_db(self.prepared_data)

    async def process_main_post(self) -> None:
        """
        Обрабатывает главный пост на странице
        """
        result = self.prepared_soup.find("div", {"class": "news-top-story__body"})
        link_and_title = result.find("a", {"class": "news-top-story__headline-link"})
        short_description = result.find("p", {"class": "news-top-story__snippet"})

        await self.add_prepared_element(
            Post(
                link=link_and_title["href"],
                title=link_and_title.text.strip(),
                short_description=short_description.text.strip()
            )
        )

    async def process_other_posts(self, post_info: PostTagInfo) -> None:
        result = self.prepared_soup.find(*post_info.block_data)
        posts = result.find_all(*post_info.post_data)
        for post in posts:
            link_and_title = post.find(*post_info.link_and_title_data)
            short_description = post.find(*post_info.short_description_data)
            await self.add_prepared_element(
                Post(
                    link=link_and_title["href"],
                    title=link_and_title["title"].strip(),
                    short_description=short_description.text.strip()
                )
            )

    async def add_prepared_element(self, new_element: Post) -> None:
        async with self.lock:
            self.prepared_data.append(
                new_element
            )
