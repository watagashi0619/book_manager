from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from db import Base, engine


class Bookshelf(Base):
    """
    本棚
    id: id
    isbn : isbn
    title : 書籍名
    publisher : 出版社
    volume : 巻数(optional)
    """

    __tablename__ = "bookshelf"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    isbn = Column("isbn", String(13), unique=True, nullable=False)
    title = Column("title", String(255))
    publisher = Column("publisher", String(255))
    volume = Column("volume", String(255))

    def __init__(
        self, isbn: str, title: str, publisher: str, volume: str,
    ):
        self.isbn = isbn
        self.title = title
        self.publisher = publisher
        self.volume = volume

    def __str__(self):
        return "<Bookshelf({},{},{},{},{})>".format(
            self.id, self.isbn, self.title, self.publisher, self.volume
        )


def main():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
