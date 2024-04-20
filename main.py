from config import BOT_TOKEN
from functions import *
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from telegram.error import BadRequest
from markups import *
from data.manager import DBManager
from message import Message
from all_respons import RequestsApi
import datetime


# Обработчик текста
async def handle_text(update, context):
    if not DBManager(str(update.effective_user.id)).get_setting_period():
        f = open("cities2.txt", encoding="utf-8")
        check = check_if_city(update.message.text, f.readlines())
        f.close()
        if check[0]:
            manager = DBManager(str(update.effective_user.id))
            manager.put_user({"current_city": check[1]})
            await update.message.reply_text(
                f"""
🌆 Выбран населенный пункт: <b>{check[1]}</b>
Что именно ты хочешь?
                """,
                parse_mode="HTML",
                reply_markup=markup_city
            )
        else:
            await update.message.reply_text(
                f"""
😭 Извините, но такого населенного пункта <b>не найдено</b>
Если Вы уверены, что ввели все верно, введите команду /add [название Вашего населенного пункта в <b>начальной форме</b>]
                        """,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="⬅️ Вернуться", callback_data="main_menu")]])
            )
    else:
        text = update.message.text
        if DBManager(str(update.effective_user.id)).get_time_repeat() is None:
            try:
                h, m = map(int, text.split(":"))
                date = datetime.time(h, m, 0, 0)

                manager = DBManager(str(update.effective_user.id))
                manager.put_user({"time_repeat": f"каждый день в {h}:{m} UTC"})
                job = context.job_queue.run_daily(period_forecast, time=date, days=(0, 1, 2, 3, 4, 5, 6),
                                                  user_id=update.effective_user.id)
                DBManager(str(update.effective_user.id)).put_user({"setting_period": False, "job_id": job.id})
                await update.message.reply_text("✅ Установлено!", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="🏠 Главное меню",
                                           callback_data="main_menu")]]))
            except ValueError:
                await update.message.reply_text("❌ Ошибка!")
                DBManager(str(update.effective_user.id)).put_user({"setting_period": False})
        else:
            time_repeat = DBManager(str(update.effective_user.id)).get_time_repeat()
            city = DBManager(str(update.effective_user.id)).get_city()
            await update.message.reply_text(
                f"❌ У вас уже настроен периодический прогноз на <b>{time_repeat}</b> для населенного пункта <b>{city}</b>!",
                parse_mode="html")


# Обработчик фото
async def handle_photo(update, context):
    if not DBManager(str(update.effective_user.id)).get_setting_period():
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        url = file.file_path
        result = ai_get_location(url)
        if result is not None:
            check = check_if_city(result, open("cities2.txt", encoding="utf-8").readlines())
            if check[0]:
                manager = DBManager(str(update.effective_user.id))
                manager.put_user({"current_city": check[1]})
                await update.message.reply_text(
                    f"""
🌆 Выбран населенный пункт: <b>{check[1]}</b>
Что именно ты хочешь?
                            """,
                    parse_mode="HTML",
                    reply_markup=markup_city
                )
            else:
                await update.message.reply_text(
                    f"""
😭 Извините, но распознавание <b>не удалось</b>
Добавить свой населенный пункт можно командой /add [название в <b>начальной форме</b>]
                        """,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⬅️ Вернуться", callback_data="main_menu")]])
                )

        else:
            await update.message.reply_text("❌ Возникла непредвиденная ошибка!")


# Добавление нового города пользователем в случае ошибки
async def add(update, context):
    if context.args:
        args = " ".join([i.lower() for i in context.args])
        with open("cities2.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{args}")
        await update.message.reply_text(
            f"✅ Населенный пункт успешно добавлен!"
        )


# Старт
async def start(update, context):
    user = update.effective_user
    DBManager(str(update.effective_user.id)).put_user({"setting_period": False})

    await update.message.reply_animation(
        animation="CgACAgIAAxkBAAICPWYEQYZ2tp5GSg6pabmnvJqaX9YoAAI9QgAC80gpSGjYntGtKMlINAQ", caption=
        f"""
<b>👋 Привет, {user.mention_html()}!</b>
Я бот, который показывает погоду (или прогноз) в Вашем населенном пункте.
<b>🌎 Выбери опцию или просто попроси погоду для своего населенного пункта 🌎</b>
Например, <i>Москва</i> или <i>покажи погоду в Москве</i>
<b>🧠 Также можно отправить фотографию места, и бот распознает его и выведет погоду 🧠</b>
<b>Для выключения периодического прогноза введи команду /cancel</b>
        """, parse_mode="HTML", reply_markup=markup_start
    )


# Отправка периодического прогноза
async def period_forecast(context):
    manager = DBManager(str(context.job.user_id))
    city = manager.get_city()
    requ = RequestsApi()
    m = Message()
    coord = requ.get_geocoder(city)
    # Формируем сообщение с прогнозом
    msg = m.weather_message(requ.get_weather(coord['coord']))
    msg = f"🌍 <b>Погода для населенного пункта {city}</b> 🌍\n\n" + msg
    await context.bot.send_message(text=msg, chat_id=context.job.user_id, parse_mode="HTML")


# Отмена периодического прогноза
async def cancel(update, context):
    if DBManager(str(update.effective_user.id)).get_time_repeat() is not None:
        job_id = DBManager(str(update.effective_user.id)).get_job_id()
        for i in context.job_queue.jobs():
            if i.id == job_id:
                i.schedule_removal()
        await update.message.reply_text(
            "❌ Периодический прогноз отменен!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🏠 Главное меню",
                                       callback_data="main_menu")]])
        )
        DBManager(str(update.effective_user.id)).put_user({"time_repeat": None})
    else:
        await update.message.reply_text(
            "❌ У вас не настроен периодический прогноз!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🏠 Главное меню",
                                       callback_data="main_menu")]])
        )


# Обработчик всех коллбеков от кнопок
async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()

    # Главное меню
    if query.data == "main_menu":
        DBManager(str(update.effective_user.id)).put_user({"setting_period": False})
        user = update.effective_user

        await query.edit_message_text(
            f"""
<b>👋 Привет, {user.mention_html()}!</b>
Я бот, который показывает погоду (или прогноз) в Вашем населенном пункте.
<b>🌎 Выбери опцию или просто попроси погоду для своего населенного пункта 🌎</b>
Например, <i>Москва</i> или <i>покажи погоду в Москве</i>
<b>🧠 Также можно отправить фотографию места, и бот распознает его и выведет погоду 🧠</b>
<b>Для выключения периодического прогноза введи команду /cancel</b>
                """, parse_mode="HTML", reply_markup=markup_start
        )
    # Настройка периодического прогноза
    elif query.data == "period":
        if DBManager(str(update.effective_user.id)).get_city() is None:
            try:
                await query.edit_message_text(
                    """
⚠️ <b>Сначала выберите населенный пункт для периодического прогноза!</b>
Чтобы это сделать, попросите погоду, а затем нажмите кнопку <b>"💡 Сделать город основным"</b>
""", parse_mode="html",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]]))
            except BadRequest:
                await update.effective_message.reply_text(
                    """
⚠️ <b>Сначала выберите населенный пункт для периодического прогноза!</b>
Чтобы это сделать, попросите погоду, а затем нажмите кнопку <b>"💡 Сделать город основным"</b>
""", parse_mode="html",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]]))
        else:
            city = DBManager(str(update.effective_user.id)).get_city()
            DBManager(str(update.effective_user.id)).put_user({"setting_period": True})

            utcnow = datetime.datetime.utcnow()
            h_utc, m_utc = utcnow.hour, utcnow.minute

            try:
                await query.edit_message_text(
                    f"""
🏘️ Город: <b>{city}</b>
⏳ Выберите периодичность на клавиатуре или напишите время в формате UTC <b>ЧЧ:ММ</b> для ежедневной отправки
🕒 UTC время на данный момент: <b>{h_utc}:{m_utc}</b>
""", reply_markup=markup_period,
                    parse_mode="html"
                )
            except BadRequest:
                await update.effective_message.reply_text(
                    f"""
🏘️ Город: <b>{city}</b>
⏳ Выберите периодичность на клавиатуре или напишите время в формате UTC <b>ЧЧ:ММ</b> для ежедневной отправки
🕒 UTC время на данный момент: <b>{h_utc}:{m_utc}</b>
""", reply_markup=markup_period,
                    parse_mode="html"
                )
    # Если человек выбрал "каждые 3 часа"
    elif query.data == "every_3_hours":
        if DBManager(str(update.effective_user.id)).get_time_repeat() is None:
            manager = DBManager(str(update.effective_user.id))
            if manager.get_setting_period():
                manager.put_user({"time_repeat": "каждые 3 часа"})
                job = context.job_queue.run_repeating(period_forecast, interval=10800, first=10800,
                                                      user_id=update.effective_user.id)
                DBManager(str(update.effective_user.id)).put_user({"setting_period": False, "job_id": job.id})
                await query.edit_message_text("✅ Установлено!", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="🏠 Главное меню",
                                           callback_data="main_menu")]]))
        else:
            time_repeat = DBManager(str(update.effective_user.id)).get_time_repeat()
            city = DBManager(str(update.effective_user.id)).get_city()
            await query.edit_message_text(
                f"❌ У вас уже настроен периодический прогноз на <b>{time_repeat}</b> для населенного пункта <b>{city}</b>!",
                parse_mode="html", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="🏠 Главное меню",
                                           callback_data="main_menu")]]))
    # Прогноз погоды по дням
    elif query.data == "everyday_forecast":
        await query.edit_message_text(
            """
📅 Выбран <b>прогноз погоды по дням</b>
На сколько дней нужен прогноз?
            """, reply_markup=markup_everyday_forecast, parse_mode="HTML"
        )
    # Возвращение в меню
    elif query.data == "back_to_city":
        await query.edit_message_text(
            f"""
🌆 Выбран населенный пункт: <b>{DBManager(str(update.effective_user.id)).get_current_city()}</b>
Что именно ты хочешь?
                    """,
            parse_mode="HTML",
            reply_markup=markup_city
        )
    # Текущий прогноз
    elif query.data == "weather_now":
        manager = DBManager(str(update.effective_user.id))
        # Получаем выбранный пользователем город
        city = manager.get_current_city()
        requ = RequestsApi()
        m = Message()
        try:
            coord = requ.get_geocoder(city)
            # И формируем сообщение с прогнозом
            msg = m.weather_message(requ.get_weather(coord['coord']))
            await query.edit_message_text(msg, parse_mode="HTML",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton(text="⬅️ Вернуться",
                                                                     callback_data="back_to_city")]]))

        except (IndexError, TypeError) as e:
            await query.edit_message_text("⚠️ Такого населенного пункта не существует!", parse_mode="HTML")
    # Обработка прогноза по дням
    elif "day" in query.data:
        time = int(query.data[0])

        requ = RequestsApi()
        m = Message()
        try:
            coord = requ.get_geocoder(DBManager(str(update.effective_user.id)).get_current_city())
            forecast = m.weather_forecast_message(requ.get_weather(coord['coord'], forecast=True, time=time))
            # Сохраняем прогноз в виде словаря в БД для быстрой работы
            DBManager(str(update.effective_user.id)).put_user({"current_forecast": forecast, "current_index": 0})

            # Первый прогноз, его дата и время
            first_forecast = forecast["list"][0]
            # Различие с UTC временем в секундах
            timezone = forecast["city"]["timezone"]

            first_date, first_time = first_forecast["dt_txt"].split()
            first_date = list(map(int, first_date.split("-")))  # [год, месяц, число]
            first_time = list(map(int, first_time.split(":")))  # [часы, минуты, секунды]

            total_date = datetime.datetime(first_date[0], first_date[1], first_date[2], first_time[0], first_time[1],
                                           first_time[2], 0) + datetime.timedelta(seconds=int(timezone))
            total_date = total_date.strftime("%d.%m.%Y %H:%M")
            first_date, first_time = total_date.split()

            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=first_date, callback_data="0")],
                    [InlineKeyboardButton(text="◀️", callback_data="previous"),
                     InlineKeyboardButton(text=first_time, callback_data="0"),
                     InlineKeyboardButton(text="▶️", callback_data="next")],
                    [InlineKeyboardButton(text="⬅️ Вернуться", callback_data="back_to_city")]
                ]
            )
            await query.edit_message_text(
                m.weather_forecast_message_normalized(
                    DBManager(str(update.effective_user.id)).get_current_forecast()["list"], 0),
                parse_mode="HTML", reply_markup=markup)
        except (IndexError, TypeError) as e:
            await query.edit_message_text("⚠️ Такого населенного пункта не существует!", parse_mode="HTML")
    # Нажатие на кнопки "вперед" и "назад"
    elif query.data == "previous" or query.data == "next":
        DBManager(str(update.effective_user.id)).put_user({"setting_period": False})
        current_index = DBManager(str(update.effective_user.id)).get_current_index()
        forecast_ = DBManager(str(update.effective_user.id)).get_current_forecast()
        if current_index - 1 < 0 and query.data == "previous":
            pass
        elif current_index + 1 == len(forecast_["list"]) and query.data == "next":
            pass
        else:
            m = Message()
            # Меняем текущий индекс прогноза, а потом обращаемся к нему из сохраненной записи
            if query.data == "previous":
                DBManager(str(update.effective_user.id)).put_user({"current_index": current_index - 1})
            else:
                DBManager(str(update.effective_user.id)).put_user({"current_index": current_index + 1})

            # Прогноз, его дата и время
            forecast = forecast_["list"][DBManager(str(update.effective_user.id)).get_current_index()]
            # Различие с UTC временем в секундах
            timezone = forecast_["city"]["timezone"]

            date, time = forecast["dt_txt"].split()
            date = list(map(int, date.split("-")))  # [год, месяц, число]
            time = list(map(int, time.split(":")))  # [часы, минуты, секунды]

            total_date = datetime.datetime(date[0], date[1], date[2], time[0],
                                           time[1],
                                           time[2], 0) + datetime.timedelta(seconds=int(timezone))
            total_date = total_date.strftime("%d.%m.%Y %H:%M")
            date, time = total_date.split()

            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=date, callback_data="0")],
                    [InlineKeyboardButton(text="◀️", callback_data="previous"),
                     InlineKeyboardButton(text=time, callback_data="0"),
                     InlineKeyboardButton(text="▶️", callback_data="next")],
                    [InlineKeyboardButton(text="⬅️ Вернуться", callback_data="back_to_city")]
                ]
            )
            # Отправляем пользователю
            await query.edit_message_text(
                m.weather_forecast_message_normalized(
                    DBManager(str(update.effective_user.id)).get_current_forecast()["list"],
                    DBManager(str(update.effective_user.id)).get_current_index()),
                parse_mode="HTML", reply_markup=markup)

    # Сделать город основным
    elif query.data == "make_city_main":
        user = DBManager(str(update.effective_user.id))
        current_city = user.get_current_city()
        user.put_user({"city": current_city})
        await query.edit_message_text(
            f"✅ Город <b>{current_city}</b> был выбран в качестве основного для периодического прогноза!",
            parse_mode="HTML", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="⬅️ Вернуться",
                                       callback_data="back_to_city")]])
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    callback = CallbackQueryHandler(callback_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(callback)
    application.add_handler(text_handler)
    application.add_handler(photo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
