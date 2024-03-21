import sqlalchemy
from . import db_session
from .users import User
from .images import Images


class DBManager:
    def __init__(self, tg_id):
        db_session.global_init('db/user.db')
        self.session = db_session.create_session()
        self.tg_id = tg_id
        if not self.get_user():
            self.create_user()

    def create_user(self) -> None:
        """создаем пользователя"""
        user = User()
        user.tg_id = self.tg_id
        self.session.add(user)
        self.session.commit()
        image = Images()
        image.user_id = self.get_user().id
        self.session.add(image)
        self.session.commit()

    def get_user(self):
        """возвращает текущего пользователя"""
        return self.session.query(User).filter(User.tg_id == self.tg_id).first()

    def put_user(self, param: dict) -> None:
        """изменяет данные пользователя, указанные в словаре ( {параметр: значение, параметр1: значение1, ...} )"""
        self.session.query(User).filter(User.tg_id == self.tg_id).update(param)
        self.session.commit()

    def get_image(self, image):
        """возвращает картинку под индексом image"""
        return eval(f'self.session.query(Images).filter(Images.user_id == self.get_user().id).first().{image}')

    def put_image(self, title, image=None) -> None:
        """изменяет картинку с индексом title на image"""
        self.session.query(Images).filter(Images.user_id == self.get_user().id).update({title: image})
        self.session.commit()

    def get_city(self) -> str:
        """возвращает название города, сохраненного пользователем"""
        return self.get_user().city

    def get_current_city(self) -> str:
        """возвращает название места, для которого пользователь хочет получить погоду"""
        return self.get_user().current_city

    def print_all(self):
        """функция для проверки работы бд (в продакшене ее не будет)"""
        return [(i.id, i.tg_id, i.city) for i in self.session.query(User).all()], [(i.id, i.user_id, i.image01) for i
                                                                                   in self.session.query(Images).all()]
