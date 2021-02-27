from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table

Base = declarative_base()


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class UrlMixin:
    url = Column(String(length=256), nullable=False, unique=True)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post.id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base, IdMixin, UrlMixin):
    __tablename__ = "post"

    title = Column(String, nullable=False)
    create_at = Column(DateTime, nullable=False)

    author_id = Column(Integer, ForeignKey("author.id"))
    author = relationship("Author")

    tags = relationship("Tag", secondary=tag_post)


class Author(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = "author"
    posts = relationship("Post")


class Tag(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = "tag"
    posts = relationship("Post", secondary=tag_post)
