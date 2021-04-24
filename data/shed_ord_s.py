import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Shedule_order(SqlAlchemyBase):
    __tablename__ = 'order_shedules'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    order = orm.relation("Order")
    time = sqlalchemy.Column(sqlalchemy.String, nullable=True)