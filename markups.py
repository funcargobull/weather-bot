from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# Главный экран
keyboard_start = [
    [InlineKeyboardButton(
        text="🌤️ Периодический прогноз", callback_data="period"
    )]
]
markup_start = InlineKeyboardMarkup(keyboard_start)

# Когда уже выбран город
keyboard_city = [
    [InlineKeyboardButton(
        text="📅 3-часовой прогноз по дням", callback_data="everyday_forecast"
    )],
    [InlineKeyboardButton(
        text="🌈 Погода на текущий момент", callback_data="weather_now"
    )],
    [InlineKeyboardButton(
        text="💡 Сделать город основным", callback_data="make_city_main"
    )],
    [InlineKeyboardButton(
        text="🏠 Главное меню", callback_data="main_menu"
    )]
]
markup_city = InlineKeyboardMarkup(keyboard_city)

# Прогноз погоды по дням
keyboard_everyday_forecast = [
    [InlineKeyboardButton(
        text="1", callback_data="1_day"
    ),
        InlineKeyboardButton(
            text="2", callback_data="2_days"
        ),
        InlineKeyboardButton(
            text="3", callback_data="3_days"
        ),
        InlineKeyboardButton(
            text="4", callback_data="4_days",
        ),
        InlineKeyboardButton(
            text="5", callback_data="5_days"
        )],
    [InlineKeyboardButton(
        text="⬅️ Вернуться", callback_data="back_to_city"
    )]
]
markup_everyday_forecast = InlineKeyboardMarkup(keyboard_everyday_forecast)

# Выбор периодичности
keyboard_period = [
    [InlineKeyboardButton(text="Каждые 3 часа", callback_data="every_3_hours")],
    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
]
markup_period = InlineKeyboardMarkup(keyboard_period)
