import sqlalchemy
from .db_session import SqlAlchemyBase


genre_book = sqlalchemy.Table(
    'genre_book',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('book', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('books.id')),
    sqlalchemy.Column('genre', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('genres.id'))
)


class Genre(SqlAlchemyBase):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)