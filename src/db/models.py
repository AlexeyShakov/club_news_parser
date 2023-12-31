from sqlalchemy.orm import relationship

from src.db.db_connection import Base
from sqlalchemy import Integer, Column, Text, Enum, ForeignKey, Date

from src.utils.enums import StepNameChoice


class Error(Base):
    """
    Описывает, на каком этапе произошла ошибка при обработке новости
    """
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    step = Column(Enum(StepNameChoice), nullable=False, unique=True)

    posts = relationship("Post", back_populates="error")


class Post(Base):
    """
    Описывает новости на сайте
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    link = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
    success_date = Column(Date, nullable=True, default=None)

    translated_title = Column(Text, nullable=True, default=None)
    translated_short_description = Column(Text, nullable=True, default=None)

    error_id = Column(Integer, ForeignKey('errors.id'), nullable=True, default=None)
    error = relationship("Error", back_populates="posts", lazy="joined")

    def to_translation_service(self) -> dict:
        return {"id": self.id, "link": self.link, "title": self.title, "short_description": self.short_description}

    def to_telegram_service(self) -> dict:
        return {"id": self.id, "link": self.link, "translated_title": self.translated_title,
                "translated_short_description": self.translated_short_description}
