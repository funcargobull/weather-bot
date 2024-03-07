import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class Images(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'images'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    # изначально строки с изображениями пустуют, это значит что требуется использовать стандартные картинки
    # если требуется заменить их, необходимо в столбцы записать изображения в бинарном виде
    image01 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image02 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image03 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image04 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image09 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image10 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image11 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image13 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image50 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relationship('User')
