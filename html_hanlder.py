class HtmlHandler:
    """
    Что нужно
    + 1. Хранить исходный html.
    + 2. Обрабатывать разную информацию - из разных тегов.
    + 3. Хранить преобразованный материал
    4. Складывать информацию в какую-то более структурированную форму,а не просто словарь?????
    5. Сохранять данные в БД
    """
    def __init__(self, initial_html: str):
        self.initial_html = initial_html
        self.prepared_data = []

    async def process_html(self):
        """
        Здесь создаем задачи для каждого типа постов на выходе должны заполнить self.prepared_data
        :return:
        """
    async def process_one_post(self, tag: str):
        """
        Есть несколько типов постов на сайте.
        1. Главная новость. Для нее используется тэг class="news-top-story block"
        2. Две новости, которые ноходятся в одном блоке с главной новостью.
        Для них используется тэг class=“grid__col news-list-featured__item”.
        3. Последние новости. Для них используется тэг class=”news-list__item”.
        Здесь мы должны обработать посты с переданными тегом.
        """
    async def save_posts_into_db(self):
        pass

