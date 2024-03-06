class Message:
    def hello_message(self) -> str:
        return '''Приветствуем вас в нашем Telegram-боте MeteorMate. 
        Пожалуйста, укажите населенный пункт, в котором вы хотите узнать погоду. 
        Он будет выбран как пункт по умолчанию. Сменить его можно будет в любой момент'''

    def wind_direction(self, deg: float or int) -> str:
        """принимает на вход метеорологические градусы и возвращает направление ветра"""
        pass

    def weater_message(self, weather: dict) -> str:  # разобраться с давлением
        return f'''Сейчас {weather['weather'][0]['description']}.
Температура воздуха {weather['main']['temp']}, ощущается как {weather['main']['feels_like']}
Атмосферное давление {weather['main']['pressure']} гПа. 
Влажность воздуха составляет {weather['main']['humidity']}%. Видимость {'не ограничена' if
        weather['visibility'] == 10000 else str(weather['visibility']) + 'метров'}.
Ветер {self.wind_direction(weather['wind']['deg'])} со скоростью {weather['wind']['speed']} м/с.'''

    def weather_forecast_message(self, weather: dict) -> str:
        message = []
        for w in weather['list']:
            message.append(f'''{w['dt_txt']}
Будет {w['weather'][0]['description']}.(стикер соответствующий) 
Температура {w['main']['temp']}, ощущается как {w['main']['feels_like']}. 
Влажность {w['main']['humidity']}%. Ветер {w['wind']['speed']} м/с.''')
        return '\n\n'.join(message)
