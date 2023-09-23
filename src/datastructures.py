from dataclasses import dataclass
from typing import TypeAlias


HTML_ENTITY: TypeAlias = tuple[str, dict[str, str]]


@dataclass
class Post:
    """
    Класс описывает пост на сайте
    """
    link: str
    title: str
    short_description: str


@dataclass
class PostTagInfo:
    """
    Класс описывает все теги, где лежит нужная информация

    Пример: block_data=("div", {"class": "something"})
    """
    block_data: HTML_ENTITY
    post_data: HTML_ENTITY
    link_and_title_data: HTML_ENTITY
    short_description_data: HTML_ENTITY


