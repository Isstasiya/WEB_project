import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.id"))
    buyer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("buyers.id"))
    complete = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    courier = orm.relation("Courier")
    buyer = orm.relation("Buyer")
    books = orm.relation("Book_buyer", back_populates='order')
    shedules = orm.relation("Shedule_order", back_populates='order')