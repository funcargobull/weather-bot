import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # название города для периодического прогноза
    current_city = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # название текущего города
    current_forecast = sqlalchemy.Column(sqlalchemy.PickleType, nullable=True)  # текущий прогноз
    current_index = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # текущий индекс прогноза
    time_repeat = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # периодичность прогноза
    setting_period = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True,
                                       default=False)  # настраивает ли периодический прогноз пользователь на данный момент
    job_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # id процесса, отвечающего за периодический прогноз
