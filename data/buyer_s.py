import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Buyer(SqlAlchemyBase):
    __tablename__ = 'buyers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    region_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("regions.id"))
    user = orm.relation("User")
    region = orm.relation("Region")
    books = orm.relation("Book_buyer", back_populates='buyer')