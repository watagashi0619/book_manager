import xml.etree.ElementTree as ET

import requests
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import desc

import db
import models

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

templates = Jinja2Templates(directory="static")
jinja_env = templates.env


class BookshelfUpdateRequest(BaseModel):
    isbn: str
    title: str
    publisher: str
    volume: str

    class Config:
        orm_mode = True


@app.get("/")
async def index(request: Request):
    bookshelf = get_bookshelf()
    return templates.TemplateResponse(
        "index.html", {"request": request, "bookshelf": bookshelf}
    )


@app.get("/get_bookinfo/{isbn}")
def book_info(isbn: str):
    return get_bookinfo(isbn)


@app.post("/update")
def update(req: BookshelfUpdateRequest):
    return update_bookshelf(req.isbn, req.title, req.publisher, req.volume)


def get_bookshelf():
    res = (
        db.session.query(models.Bookshelf)
        .order_by(desc(models.Bookshelf.title), desc(models.Bookshelf.isbn))
        .all()
    )
    db.session.close()
    return res


def update_bookshelf(isbn: str, title: str, publisher: str, volume: str):
    book = models.Bookshelf(isbn=isbn, title=title, publisher=publisher, volume=volume)

    is_not_exists = not db.session.query(
        db.session.query(models.Bookshelf)
        .filter(models.Bookshelf.isbn == isbn)
        .exists()
    ).scalar()
    if is_not_exists:
        db.session.add(book)
        db.session.commit()
    db.session.close()

    return is_not_exists


def get_bookinfo(isbn: str):
    result = _opendb(isbn)
    if result == {}:
        result = _ndl(isbn)
    return result


def _ndl(isbn: str):
    api_url = "https://iss.ndl.go.jp/api/sru?operation=searchRetrieve&maximumRecords=1&recordPacking=xml&onlyBib=true&query=isbn%3d%22{}%22".format(
        isbn
    )
    req = requests.get(api_url)
    root = ET.fromstring(req.content)

    try:
        title = next(root.iter("{http://purl.org/dc/elements/1.1/}title")).text
        publisher = next(root.iter("{http://purl.org/dc/elements/1.1/}publisher")).text
        volume = ""

        result = {
            "isbn": isbn,
            "title": title,
            "publisher": publisher,
            "volume": volume,
        }

        return result
    except:
        return {}


def _opendb(isbn: str):
    api_url = "https://api.openbd.jp/v1/get?isbn={}".format(isbn)
    req = requests.get(api_url)
    data = req.json()[0]
    try:
        title = data["summary"]["title"]
        publisher = data["summary"]["publisher"]
        title_element = data["onix"]["DescriptiveDetail"]["TitleDetail"]["TitleElement"]
        volume = title_element["PartNumber"] if "PartNumber" in title_element else ""

        result = {
            "isbn": isbn,
            "title": title,
            "publisher": publisher,
            "volume": volume,
        }

        return result
    except:
        return {}
