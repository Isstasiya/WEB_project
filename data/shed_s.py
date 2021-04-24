import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Shedule(SqlAlchemyBase):
    __tablename__ = 'shedules'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.id"))
    courier = orm.relation("Courier")
    time = sqlalchemy.Column(sqlalchemy.String, nullable=True)