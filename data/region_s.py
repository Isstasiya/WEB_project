import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


region_courier = sqlalchemy.Table(
    'region_courier',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('region', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('regions.id')),
    sqlalchemy.Column('courier', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('couriers.id'))
)


class Region(SqlAlchemyBase):
    __tablename__ = 'regions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    region_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    buyer = orm.relation("Buyer", back_populates='region')