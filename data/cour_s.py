import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    earnings = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    assign_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    raz_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation("User")
    shedules = orm.relation("Shedule", back_populates='courier')
    regions = orm.relation("Region",
                          secondary="region_courier",
                          backref="courier")
    orders = orm.relation("Order", back_populates='courier')