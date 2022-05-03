from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

RDB_PATH = "sqlite:///bookshelf_db.sqlite3"

engine = create_engine(RDB_PATH, future=True, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
