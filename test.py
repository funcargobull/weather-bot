from data.manager import DBManager


manager = DBManager('123')
manager.put_image('image01')
print(manager.get_current_city())
print(manager.print_all())