import requests
from PIL import Image
from io import BytesIO
class RequestsApi:
    def __init__(self):
        self.geo_apikey = '40d1649f-0493-4b70-98ba-98533de7710b'
        self.weather_apikey = '4201889683d67010c85addd95be4e7d5'

    def get_weather(self, coord: tuple, forecast=False, time=5) -> dict:
        """выводит словарь значений погоды. coord - координаты места, где вы хотите узнать погоду,
        forecast - нужен прогноз (True) или погода на текущий момент (False),
        time - на сколько дней необходим прогноз (не более 5)"""
        if forecast:
            req = 'https://api.openweathermap.org/data/2.5/forecast'
            params = {'lat': coord[0], 'lon': coord[1], 'appid': self.weather_apikey,
                      'units': 'metric', 'cnt': time, 'lang': 'ru'}
            response = requests.get(req, params=params)
            if response:
                json_response = response.json()
                return json_response
            else:
                return {'message': 'error'}
        else:
            req = 'https://api.openweathermap.org/data/2.5/weather'
            params = {'lat': coord[0], 'lon': coord[1], 'appid': self.weather_apikey, 'units': 'metric', 'lang': 'ru'}
            response = requests.get(req, params=params)
            if response:
                json_response = response.json()
                return json_response
            else:
                return {'message': 'error'}

    def get_weather_map(self, coord: tuple):
        x, y = coord
        req = f'https://tile.openweathermap.org/map/precipitation_new/9/{x}/{y}.png?appid={self.weather_apikey}'
        response = requests.get(req)
        if response:
            #  print(response.content)
            Image.open(BytesIO(
                response.content)).show()
        else:
            return {'message': 'error'}

    def get_geocoder(self, title: str) -> dict:
        req = 'https://geocode-maps.yandex.ru/1.x'
        params = {'apikey': self.geo_apikey, 'geocode': title, 'format': 'json'}
        response = requests.get(req, params=params)
        if response:
            json_response = response.json()
            # Получаем топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            return {'address': toponym_address, 'coord': tuple(toponym_coodrinates.split())}
        else:
            return {'message': 'error'}


'''requ = RequestsApi()

requ.get_weather_map(('37', "55"))'''
