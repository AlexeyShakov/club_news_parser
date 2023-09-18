import asyncio

from bs4 import BeautifulSoup

from datastructures import Post, PostTagInfo


class HtmlHandler:
    """
    Что нужно
    + 1. Хранить исходный html.
    + 2. Обрабатывать разную информацию - из разных тегов.
    + 3. Хранить преобразованный материал
    4. Складывать информацию в какую-то более структурированную форму,а не просто словарь?????
    5. Сохранять данные в БД
    """
    def __init__(self, prepared_soup: BeautifulSoup):
        self.prepared_soup = prepared_soup
        self.prepared_data = []


    async def process_html(self):
        """
        Здесь создаем задачи для каждого типа постов на выходе должны заполнить self.prepared_data
        :return:
        """
        # КОД ОТРАБАТЫВАЕТ НЕВЕРНО!!!!!!! ПОПРОБОВАТЬ ЗАВТРА ЗАПУСТИТЬ 3 таски раздельно!!!
        # Нужно сделать так, чтобы единовременно в список могла писать одна корутиина
        featured_news = PostTagInfo(
            block_data=("div", {"class": "grid news-list-featured block"}),
            post_data=("div", {"class": "grid__col news-list-featured__item"}),
            link_and_title_data=("a", {"class": "news-list-featured__figure"}),
            short_description_data=("p", {"class": "news-list-featured__snippet"})

        )
        latest_news = PostTagInfo(
            block_data=("div", {"class": "news-list block"}),
            post_data=("div", {"class": "news-list__item "}),
            link_and_title_data=("a", {"news-list__figure": ""}),
            short_description_data=("p", {"class": "news-list__snippet"})
        )
        main_news_task = asyncio.create_task(self.process_main_post())
        features_news_task = asyncio.create_task(self.process_other_posts(featured_news))
        latest_news_task = asyncio.create_task(self.process_other_posts(latest_news))
        await asyncio.gather(main_news_task, features_news_task, latest_news_task)


    async def process_main_post(self):
        """
        Есть несколько типов постов на сайте.
        + 1. Главная новость. Для нее используется тэг class="news-top-story__body"
        + 2. Две новости, которые ноходятся в одном блоке с главной новостью.
        Для них используется тэг class=“grid__col news-list-featured__item”.
        3. Последние новости. Для них используется тэг class=”news-list__item”.
        Здесь мы должны обработать посты с переданными тегом.
        """
        result = self.prepared_soup.find("div", {"class": "news-top-story__body"})
        link_and_title = result.find("a", {"class": "news-top-story__headline-link"})
        short_description = result.find("p", {"class": "news-top-story__snippet"})
        self.prepared_data.append(
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
            self.prepared_data.append(
                Post(
                    link=link_and_title["href"],
                    title=link_and_title["title"].strip(),
                    short_description=short_description.text.strip()
                )
            )

    async def save_posts_into_db(self):
        pass

