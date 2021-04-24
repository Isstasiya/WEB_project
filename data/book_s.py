import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    like = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dislike = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    buyers = orm.relation("Book_buyer", back_populates='book')
    genres = orm.relation("Genre",
                          secondary="genre_book",
                          backref="book")