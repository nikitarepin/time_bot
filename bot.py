# _______________________________________________БИБЛИОТЕКИ_____________________________________________________________
# библиотки для работы бота:
import time
import logging
from aiogram import Bot, Dispatcher, types, executor
import datetime
import sqlite3
import pandas as pd
import csv
from tabulate import tabulate

# _______________________________________________БАЗА_ДАННЫХ____________________________________________________________

# создание базы данных
base = sqlite3.connect('time_working_bot.db')
cursor = base.cursor()

# создание таблицы
base.execute(
    "CREATE TABLE IF NOT EXISTS {} (id, time_working_hours INT, time_working_minets INT, today INT, week_today INT, "
    "month_today INT, year_today INT)".format('time_working_bot'))
base.commit()

# _______________________________________________ФУНКЦИИ________________________________________________________________


# _________________________________ВРЕМЯ

# переменные для подсчета времени
_time_ = []
result = 0


# костыль для подсчета времени
def check_time():
    global result
    if len(_time_) >= 2:
        _time_.clear()
    _time_.append(time.time())

    if len(_time_) == 2:
        result = _time_[-1] - _time_[0]

    return result


# _________________________________НАЧАЛЬНАЯ СТРАНИЦА

# функция для создания кнопок начальной старницы ("старт", "статистика за неделю", "статистика за месяц")
def create_mark():
    mark_start = types.KeyboardButton(text='Start', callback_data="Start")
    mark_stats_week = types.KeyboardButton(text="Week's stats 📑", callback_data="Week's stats 📑")
    mark_stats_month = types.KeyboardButton(text="Month's stats 🗂", callback_data="Month's stats 🗂")
    mark_donate = types.KeyboardButton(text="💸")
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(mark_start, mark_stats_week, mark_stats_month, mark_donate)
    return mark


# _________________________________END

# создадим кнопку end для завершения работы
def create_end():
    mark_end = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_end_work = types.KeyboardButton("End")
    mark_end.add(mark_end_work)
    return mark_end


# _________________________________ДА\НЕТ

# функция для создания кнопок "да" и "нет", чтобы узнать будет ли человек сегодня еще работать
def create_yes_no():
    yes_no_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
    inline_button_yes = types.KeyboardButton(text='Да', callback_data='yes')
    inline_button_no = types.KeyboardButton('Нет', callback_data='no')
    yes_no_button.add(inline_button_yes, inline_button_no)
    return yes_no_button


# _________________________________МИНУТЫ=>ЧАСЫ

# переведем минуты в часы
def minets_in_hours(hours, minets):
    if minets >= 60:
        hours += minets // 60
        minets = minets % 60
    return hours, minets


# _________________________________СТАТИСТИКА_КОЛИЧЕСТВА_ЮЗЕРОВ
# список пользователей
user_data = []

# внесем список пользователей из csv файла на тот случай, если программа перезапустится
with open("users.csv", "r") as file:
    reader = csv.reader(file)

    for line in reader:
        user_data.append(line)


def main_statics(user):

    # вызов функции статистики пользователей за недею
    statics_week(user)

    # проверка есть ли пользователь уже в списке
    data_table = pd.read_csv("users.csv")
    # если пользователь уже есть в списке, то мы прервем функцию
    if user[0] in data_table:
        return None

    # добавление пользователя в список и обновление csv файла
    user_data.append([f'{user}'])
    with open("users.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            user_data
        )


# _________________________________СТАТИСТИКА_ЮЗЕРОВ_СДЕЛАВШИХ_РАБОЧИЙ_ЦИКЛ
# список пользователей
user_work_data = []

# внесем список пользователей из csv файла на тот случай, если программа перезапустится
with open("users_work.csv", "r") as file:
    reader = csv.reader(file)

    for line in reader:
        user_work_data.append(line)


def statics_work_user(user):
    # проверка есть ли пользователь уже в списке
    data_table = pd.read_csv("users_work.csv")
    # если пользователь уже есть в списке, то мы прервем функцию
    if user[0] in data_table:
        return None

    # добавление пользователя в список и обновление csv файла
    user_work_data.append([f'{user}'])
    with open("users_work.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            user_work_data
        )


# _________________________________СТАТИСТИКА_ЮЗЕРОВ_НАЖАВШИХ_КНОПКУ_ДОНАТ
# список пользователей
user_donate_data = []

# внесем список пользователей из csv файла на тот случай, если программа перезапустится
with open("users_donate.csv", "r") as file:
    reader = csv.reader(file)

    for line in reader:
        user_donate_data.append(line)


def statics_donate(user):
    # добавление пользователя в список и обновление csv файла
    user_donate_data.append([f'{user}'])
    with open("users_donate.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            user_donate_data
        )


# _________________________________СТАТИСТИКА_КОЛИЧЕСТВА_ЮЗЕРОВ_ЗА_НЕДЕЛЮ
def statics_week(user):
    # посмотрим какая сейчас неделя
    week_today = datetime.date.today()
    week_today = int(week_today.isocalendar()[1])

    # возьмем сегодняшнюю дату
    today = int(datetime.date.today().day)

    # список пользователей
    user_week_data = []

    # возьмем номер недели (он хранится в файле)
    with open("users_week.csv", "r") as file:
        reader = csv.reader(file)

        for line in reader:
            week_yesterday = int(line[0])
            break

    if week_yesterday != week_today:
        user_week_data.append([f'{week_today}', '0'])
    else:
        with open("users_week.csv", "r") as file:
            reader = csv.reader(file)

            for line in reader:
                user_week_data.append(line)

    # добавим пользователя в статистику
    user_week_data.append([f'{user}', f'{today}'])
    with open("users_week.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(
            user_week_data
        )


# _______________________________________________ТОКЕН__________________________________________________________________
# токен
bot = Bot(token="5574438443:AAGkNGCg2XqwsdnbGMA6G2p-1Vs1KueU-4s")
dp = Dispatcher(bot)


# _______________________________________________КОД____________________________________________________________________


# программа начнет работать с команды start
# бот выдаст приветствие и кнопки для начала работы с ботом (старт, статистика за неделю, статистика за месяц)
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    # возьмем имя пользователя для его приветствия
    user_first_name = message.from_user.first_name
    logging.info(f' {user_first_name} {time.asctime()}')  # я пока не знаю зачем нам logging, как разберусь,
    # то доработаю

    # получим id пользователя, чтобы добавить в csv файл
    user_id = str(message.from_user.id)

    # добавим id в csv
    main_statics(user_id)

    # создадим кнопки для начальной страницы
    mark = create_mark()

    # выведем приветстиве пользователя, сообщение о функционале бота и кнопки для работы с ботом
    await message.answer(
        f'Привет {user_first_name}. Это бот, который поможет отслеживать стастику времени за работой\n'
        f'\n'
        f'Помимо твоего ежедневного отчета, можно посмотреть статистику за неделю и месяц! 😉')
    await message.answer(
        f"ᅠ ᅠ ᅠ ⚙️Команды:\n"
        f"▶ Start - начать рабочую сессию\n"
        f"⏹ End - закончить рабочую сессию\n"
        f"↩ Week's stats - стастика за неделю\n"
        f"🔁 Month's stats - статистика за месяц",
        reply_markup=mark)


# бот открывает "режим работы" и после его завершения возвращает пользователя в меню
# в данном режиме доступна только кнопка end
@dp.message_handler(content_types=['text'])
async def work(message):
    # возьмем первое имя пользователя для отправки сообщения
    user_first_name = message.from_user.first_name

    # создадим кнопку end и зафиксируем время начала работы
    if message.text == 'Start':
        mark_end = create_end()
        check_time()

        # отправим сообщение и дадим пользователю кнопку end для завершения работы
        await message.answer(f'Проведи это время продуктивно, {user_first_name}! 🚀',
                             reply_markup=mark_end)

    # после нажатия кнопки end откроется первоначальное меню
    # также id, часы, минуты работы и сегодняшняя дата-неделя-месяц-год добавятся в базу данных
    if message.text == "End":
        # спросим у пользователя будет ли он сегодня еще работать
        # для этого создадим две кнопки "да" и "нет"
        yes_no_button = create_yes_no()

        # зафиксируем время окончания работы
        check_time()

        # переведем результат работы пользователя в часы : минуты : секунды
        result_hour = round(result // 3600)
        result_minets = round((result % 3600) // 60)
        result_seconds = round(result % 60)

        # возьмем id пользователя, чтобы создать ячейку в таблице
        bot_id = str(message.from_user.id)

        # возьмем тип данных string, чтобы записать данные о времени работы в таблицу бд
        bot_time_working_hours = str(result_hour)
        bot_time_working_minets = str(result_minets)

        # возьмем данные дня, недели, месяца и года в цифрах, чтобы записать в базу данных
        date_week_cloud = datetime.date.today()
        date_week = int(date_week_cloud.isocalendar()[1])
        date_month = int(datetime.date.today().month)
        date_year = int(datetime.date.today().year)
        today = int(datetime.date.today().day)

        # заполним таблицу
        cursor.execute('INSERT INTO time_working_bot VALUES (?, ?, ?, ?, ?, ?, ?)', (
            bot_id, bot_time_working_hours, bot_time_working_minets, today, date_week, date_month, date_year))
        base.commit()

        # выведем сообщение с результатом работы, которую пользователь сейчас закончил
        await message.answer(
            f'🦁 {user_first_name}, ты работал {result_hour} ч : {result_minets} мин : {result_seconds} с')

        # cпросим у юзера закончил он работать на сегодня или нет
        await message.reply(f'Ты планируешь сегодня еще поработать? 🏰', reply_markup=yes_no_button)

    # проверим будет ответ на вопрос о конце работы "да" или "нет"
    # если да, то мы скажем пользователю отдохнуть и вернуться
    if message.text == 'Да':
        # вернем пользователя в начальную страницу, чтобы он мог снова нажать start
        mark = create_mark()

        # выведем сообщение и начальную страницу
        await message.answer('Хорошо, сделай перерыв и возвращайся 🧑🏼‍💻', reply_markup=mark)

    # если ответ нет, то есть сегодня юзер больше работать не будет, то выведет статы за день и похвалим за
    # хорошую работу, а также вернем в начальную страницу
    if message.text == 'Нет':

        # вернем пользователя в начальную страницу после окончания работы
        mark = create_mark()

        # возьмем номер месяца и года(чтобы чистить таблицу от старых данных)
        today_month = int(datetime.date.today().month)
        today_year = int(datetime.date.today().year)

        # удалим лишние данные за прошлые месяцы
        cursor.execute("DELETE FROM time_working_bot WHERE month_today < ? or year_today < ?",
                       (today_month, today_year,))
        base.commit()

        # возьмем данные о дате, чтобы вывести статы за сегодня
        today = int(datetime.date.today().day)

        # возьмеме id юзера
        user_id = str(message.from_user.id)

        # добавим пользователя в стастику (список пользователей, сделавших полную рабочую сессию)
        statics_work_user(user_id)

        # сделаем список под часы и минуты
        today_hour = []
        today_minets = []

        # возьмем строки, где записано сколько ЧАСОВ пользователь сегодня работал
        cursor.execute('SELECT time_working_hours FROM time_working_bot WHERE id == ? and today == ?',
                       (user_id, today,))
        rows = cursor.fetchall()

        # заполним список ЧАСАМИ проведенными за работой
        for row in rows:
            today_hour.append(int(''.join(map(str, row))))

        # сделаем промежуточные рассчеты по сумме часов
        result_today_hours = sum(today_hour)

        # возьмем строки, где записано сколько МИНУТ работал юзер
        cursor.execute('SELECT time_working_minets FROM time_working_bot WHERE id == ? and today == ?',
                       (user_id, today,))
        rows = cursor.fetchall()

        # заполним список МИНУТАМИ работы
        for row in rows:
            today_minets.append(int(''.join(map(str, row))))

        # посчитаем итоговое кол-во работы в минутах и часах
        result_today_minets = sum(today_minets)

        # посчитаем итоговое кол-во часов и минут
        result_today_hours, result_today_minets = minets_in_hours(result_today_hours, result_today_minets)

        # вывод сообщения с итогами работы за сегодня
        await message.answer(f'👻 Сегодня ты работал {result_today_hours} ч : {result_today_minets} мин',
                             reply_markup=mark)

        # дадим юзеру медальку за хорошую работу
        if result_today_hours > 4:
            await message.answer(f"Ты молодец! Держи медальку за свою работу ☺")
            await message.answer_sticker(
                r'CAACAgIAAxkBAAEGS1hjY42-OBYJTXavT2dpo1VZHw3T8gACSBsAAkPgIUtBdQPtOKSdByoE')

    # вывод пользователю статистики за неделю
    if message.text == "Week's stats 📑":

        # возьмем id пользователя, чтобы посмотреть его статистику в базе данных
        user_id = str(message.from_user.id)

        # сосздадим список под результаты (часы)
        week_stats_hours = []

        # создадим список под результаты (минуты)
        week_stats_minets = []

        # возьмем номер этой недели
        today_week = datetime.date.today()
        today_week = today_week.isocalendar()[1]

        # возьмем номер месяца и года(чтобы чистить таблицу от старых данных)
        today_month = int(datetime.date.today().month)
        today_year = int(datetime.date.today().year)

        # удалим лишние данные за прошлые месяцы
        cursor.execute("DELETE FROM time_working_bot WHERE month_today < ? or year_today < ?",
                       (today_month, today_year,))
        base.commit()

        # возьмем количество строк с данными о проведеныых ЧАСАХ за роботой из таблицы с помощью id пользователя
        cursor.execute("SELECT time_working_hours FROM time_working_bot WHERE id == ? and week_today == ?",
                       (user_id, today_week,))
        rows = cursor.fetchall()

        # достанем из таблицы данные о том, сколько часов проработал пользователь и поместим в список
        for row in rows:
            week_stats_hours.append(int(''.join(map(str, row))))

        # посчитаем промежуточный результат работы за неделю (промежуточный, потому что еще минуты сформируют
        # в сумме определенное количество часов)
        result_week_hours = sum(week_stats_hours)

        # возьмем количество сторк с данными о проведенных МИНУТАХ за роботой пользовтеля
        cursor.execute("SELECT time_working_minets FROM time_working_bot WHERE id == ? and week_today == ?",
                       (user_id, today_week,))
        rows = cursor.fetchall()

        # достанем из таблицы данные о том, сколько минут провел пользователь за работой
        for row in rows:
            week_stats_minets.append(int(''.join(map(str, row))))

        # посчитаем общее количество минут
        result_week_minets = sum(week_stats_minets)

        # посчитаем итоговое кол-во часов и минут
        result_week_hors, result_week_minets = minets_in_hours(result_week_hours, result_week_minets)

        # вернем пользователя в начальную страницу после окончания работы
        mark = create_mark()

        await message.answer(f"📑📑📑\n"
                             f"За неделю ты работал:\n"
                             f"____________________________\n"
                             f"{result_week_hours} часов : {result_week_minets} минyт\n"
                             f"____________________________", reply_markup=mark)

    # сделаем вывод статистики за месяц
    if message.text == "Month's stats 🗂":

        # возьмем id юзера для поиска его данных
        user_id = str(message.from_user.id)

        # сосздадим список под результаты (часы)
        month_stats_hours = []

        # создадим список под результаты (минуты)
        month_stats_minets = []

        # возьмем номер месяца и года, чтобы найти данные и удалить лишние
        today_month = int(datetime.date.today().month)
        today_year = int(datetime.date.today().year)

        # удалим лишние данные за прошлые месяцы
        cursor.execute("DELETE FROM time_working_bot WHERE month_today < ? or year_today < ?",
                       (today_month, today_year,))
        base.commit()

        # возьмем количество строк с данными о проведеныых ЧАСАХ за роботой из таблицы с помощью id пользователя
        cursor.execute("SELECT time_working_hours FROM time_working_bot WHERE id == ? and month_today == ?",
                       (user_id, today_month,))
        rows = cursor.fetchall()

        # достанем из таблицы данные о том, сколько часов проработал пользователь и поместим в список
        for row in rows:
            month_stats_hours.append(int(''.join(map(str, row))))

        # посчитаем промежуточный результат работы за неделю (промежуточный, потому что еще минуты сформируют
        # в сумме определенное количество часов)
        result_month_hours = sum(month_stats_hours)

        # возьмем количество сторк с данными о проведенных МИНУТАХ за роботой пользовтеля
        cursor.execute("SELECT time_working_minets FROM time_working_bot WHERE id == ? and month_today == ?",
                       (user_id, today_month,))
        rows = cursor.fetchall()

        # достанем из таблицы данные о том, сколько минут провел пользователь за работой
        for row in rows:
            month_stats_minets.append(int(''.join(map(str, row))))

        # посчитаем общее количество минут
        result_month_minets = sum(month_stats_minets)

        # посчитаем итоговое кол-во часов и минут
        result_month_hours, result_month_minets = minets_in_hours(result_month_hours, result_month_minets)

        # вернем пользователя в начальную страницу после окончания работы
        mark = create_mark()

        await message.answer(f"🗂🗂🗂\n"
                             f"В этом месяце ты инвестировал в работу:\n"
                             f"____________________________\n"
                             f"{result_month_hours} ч : {result_month_minets} мин\n"
                             f"____________________________",
                             reply_markup=mark)

    # кнопка под донат
    if message.text == "💸":
        # создание самой кнопки под донат
        mark_donate = types.InlineKeyboardMarkup()
        mark_donate_inline = types.InlineKeyboardButton("💸", url="t.me/donat_time_working_bot")
        mark_donate.add(mark_donate_inline)

        # возьмем id пользователя, чтобы добавить его в статистику
        user_id = message.from_user.id

        # добавим юзера в статистику
        statics_donate(user_id)

        # вернем начальную страницу
        mark = create_mark()

        # романтичное послание юзеру
        await message.answer(f'Создать этого бота было непросто, но я сделал это! 😌 Потому что мне не хватало '
                             'именно такого функционала...\n'
                             '\n'
                             'Рекламу, я кстати, в бота вставлять не стал 🙂'
                             '\n'
                             'Если бот делает процесс твоей работы удобнее или чего-то не хватает, то можешь '
                             'прикрепить свой комментарий к донату (даже от 10₽)\n'
                             '\n'
                             'Я увижу твою мысль 😉\n'
                             'Возможно, ты повлияешь на дальнешее развитие этого проекта',
                             reply_markup=mark)

        # вывод кнопки под донат
        await message.answer('Отправить donate можно по кнопке "💸" под этим сообщением ', reply_markup=mark_donate)

    # вывод статистики по общему количеству пользователей
    if message.text == "Stat_time_bot_1978":

        # статистика по общему количеству пользователей
        main_results = pd.read_csv("users.csv")

        # статистика по общему количеству пользователей, сделавших полный рабочий цикл
        work_results = pd.read_csv("users_work.csv")

        # статистика по общему количеству пользователей, нажавших кнопку донат
        donate_results = pd.read_csv("users_donate.csv")

        # вывод общей статистики
        await message.answer(f'All: {len(main_results) : 15} users\n'
                             f'Work: {len(work_results) : 10} users\n'
                             f'Donate: {len(donate_results) : 6} users\n'
                             f'\n'
                             f'Statistics of new users for the week ⬇️')

        # статистика по количеству пользователей за неделю по дням

        # посмотрим номер сегодняшней недели, чтобы учесть это при чтении файла
        week_today = datetime.date.today()
        week_today = int(week_today.isocalendar()[1])

        # переменные для хранения в памяти дня и результатов статистики за день
        date = 0
        res_day = 0

        # создание таблицы для вывода
        table = [('Data:', 'Users:')]

        with open("users_week.csv", "r") as file:
            reader = csv.reader(file)

            for line in reader:
                if int(line[0]) == week_today:
                    continue
                if date != int(line[1]):
                    if date != 0:
                        table.append((f'{date}', f'{res_day}'))
                    date = int(line[1])
                    res_day = 1
                else:
                    res_day += 1

            table.append((f'{date}', f'{res_day}'))

        # зададим внешние параметры для таблицы
        table = tabulate(table, headers='firstrow', stralign='center')

        await message.answer(f'{table}')






# запуск программы
if __name__ == '__main__':
    executor.start_polling(dp)
