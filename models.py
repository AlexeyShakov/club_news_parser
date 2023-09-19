from db_connection import Base
from sqlalchemy import Integer, Column, Text

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    link = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
