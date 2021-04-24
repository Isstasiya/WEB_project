import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Book_buyer(SqlAlchemyBase):
    __tablename__ = 'book_buyers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    book_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books.id"))
    buyer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("buyers.id"))
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    book = orm.relation("Book")
    buyer = orm.relation("Buyer")
    order = orm.relation("Order")