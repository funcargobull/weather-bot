class Message:
    def wind_direction(self, deg: float or int) -> str:
        """переводит из метеорологических градусов в строку с названием ветра"""
        direction = ['Северный', 'Северо-восточный', 'Восточный', 'Юго-восточный', 'Южный', 'Юго-западный', 'Западный',
                     'Северо-западный']
        value = int(deg / 22.5 + 1) // 2
        return direction[value if value < 8 else 0]

    def weather_message(self, weather: dict) -> str:
        """возвращает сообщение с информацией о текущей погоде"""
        msg = f'''🌈 Сейчас <b>{weather['weather'][0]['description']}</b>.
🌡 Температура воздуха <b>{int(weather['main']['temp'])}°C</b>, ощущается как <b>{int(weather['main']['feels_like'])}°C</b>
🌫️ Атмосферное давление <b>{int(weather['main']['pressure'] * 0.75)}</b> мм рт.ст. 
💨 Ветер <b>{self.wind_direction(weather['wind']['deg'])}</b> со скоростью <b>{weather['wind']['speed']} м/с.</b>
💧 Влажность воздуха составляет <b>{weather['main']['humidity']}%</b>. '''
        try:
            msg += f"Видимость {'<b>не ограничена</b>' if weather['visibility'] == 10000 else str(weather['visibility']) + ' метров'}."
        except KeyError:
            pass

        return msg

    def weather_forecast_message(self, weather: dict):
        """возвращает прогноз"""
        return weather

    def weather_forecast_message_normalized(self, weather: dict, index: int) -> str:
        """возвращает сообщение с информацией о прогнозе погоды"""
        w = weather[index]
        return f'''
Будет <b>{w['weather'][0]['description']}</b>.
Температура <b>{int(w['main']['temp'])}°C</b>, ощущается как <b>{int(w['main']['feels_like'])}°C</b>.
Влажность <b>{w['main']['humidity']}%</b>. Ветер <b>{w['wind']['speed']} м/с</b>.
'''
