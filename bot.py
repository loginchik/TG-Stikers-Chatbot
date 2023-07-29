import random
import os, dotenv
import json
import sqlite3

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor, exceptions
import aiogram
from bs4 import BeautifulSoup

# import emoji

# Read the token from .env file 
# IMPORTANT: never share the token, otherwise the bot can be stollen. 
dotenv.load_dotenv()
token = os.getenv('DEMO_TOKEN')

# Create bot and dispatcher 
bot = Bot(token)
dp = Dispatcher(bot=bot)

# Load message templates from json file
with open('message_templates.json') as templates_file:
    message_templates = json.load(templates_file)
# Set default user locale 
user_locale = 'en'

# Обозначение словаря со стикерами
# Словарь в формате {emoji: [sticker_id, sticker_id]}
stickers = dict()

# Файл с названиями используемых стикерпаков
sets_filename = 'sets.txt'


def get_used_sets():
    # Получает список используемых стикерпаков из файла

    # Открытие файла
    with open(sets_filename, 'r') as sets_file:
        # Создание списка
        sets = [line.strip() for line in sets_file.read().split('\n')]

    # Возвращение списка используемых стикерпаков (только названия)
    return sets


def write_new_set(new_set):
    # Записывает название нового стикерпака в файл со всеми паками

    # Открывает файл
    with open(sets_filename, 'a') as sets_file:
        # Дописывает название в конец
        sets_file.write(f'{new_set}\n')


async def download_stickers_to_use():
    # Загрузка в словарь со стикерами стикеров для использования

    # Глобальный словарь со стикерами
    global stickers

    # Перебор названий паков из файла
    for stick_set in get_used_sets():
        try:
            # Получение информации о сете
            curr_set = await bot.get_sticker_set(stick_set)
        except exceptions.InvalidStickersSet:
            # Пропуск ошибочных сетов
            continue

        # Получение набора стикеров из информации о сете
        cur_stickers = curr_set.stickers

        # Перебор стикеров из сета
        for stick in cur_stickers:
            # Если эмоджи этого стикера нет в словаре стикеров
            if stick.emoji not in stickers.keys():
                # Создается новый ключ со словарем из одного стикера
                stickers[stick.emoji] = [stick.file_id]
            else:
                # Иначе дополняется словарь эмоджи
                stickers[stick.emoji].append(stick.file_id)

    # Исключение повторяющихся стикеров из словаря стикеров
    for key in stickers.keys():
        key = list(set(stickers[key]))


def update_sets():
    # Подгружает стикерпаки с сайта

    # Создание запроса и получение содержимого страницы
    page = requests.get('https://tlgrm.ru/stickers')
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')

    # Список всех ссылок на стикерпаки с сайта
    all_a = [a.get('href') for a in soup.find_all(class_='stickers-snippet-item')]

    # Получение из ссылок названий стикерпаков (последний фрагмент ссылки)
    new_sets = [tag.split('/')[-1] for tag in all_a]

    # Получение списка используемых паков
    used_sets = get_used_sets()

    # Перебор новых паков с сайта
    for pack in new_sets:
        # Добавление тех, которые еще не используются, в список всех паков
        if pack not in used_sets:
            write_new_set(pack)


async def startup(_):
    # Функция при запуске бота

    # Подгружает новые стикерпаки с сайта
    update_sets()
    # Загружает словарь со стикерами
    await download_stickers_to_use()
    # Сообщает о готовности бота к работе в терминале
    print('Готов к работе!')


@dp.message_handler(content_types=['sticker'])
# Реагирует на все входящие стикеры
async def get_sticker_set(message: types.Message):
    # Глобальный словарь со стикерами по эмоджи
    global stickers
    
    print(message.from_user.language_code)

    # Определение пользовательского стикера
    user_sticker = message.sticker
    # print(user_sticker)
    # Определение стикерпака, в котором пользовательский стикер
    set_name = user_sticker.set_name
    set_data = await bot.get_sticker_set(name=user_sticker.set_name)
    # print(set_data)
    
    if set_name != 'None' and set_data['sticker_type'] == 'regular':
        this_name = set_data['name']
        this_is_animated = set_data['is_animated']
        if this_is_animated:
            this_animated_status = 1
        else: 
            this_animated_status = 0
        this_stick_count = len(set_data['stickers'])
        print(f'Received stickerpack data: {this_name}, {this_animated_status}, {this_stick_count}')
    else:
        print('Set is not aropriate')

    # Если этот стикерпак возможно сохранить в программу
    if set_name != 'None':
        # Получение списка всех используемых в программе стикерпаков
        sets = get_used_sets()
        # Если этого стикера нет
        if set_name not in sets:
            # Уведомление пользователя
            await bot.send_message(chat_id=message.chat.id,
                                   text=message_templates[user_locale]['save sticker'])
            # Запись стикерпака в список для программы
            write_new_set(set_name)
            # Перезагрузка словаря со стикерами, чтобы включить туда новый пак
            await download_stickers_to_use()

    # Определение эмоджи, соответствующего пользовательскому стикеру
    user_emoji = user_sticker.emoji
    # print(user_emoji)
    # print(emoji.demojize(user_emoji))
    # print(emoji.emojize(emoji.demojize(user_emoji)))

    # Если возможно дать ответ на этот стикер
    if user_emoji in stickers.keys():
        # Выбор рандомного подходящего стикера
        random_sticker = random.choice(stickers[user_emoji])
        # Отправка
        await bot.send_sticker(chat_id=message.chat.id,
                               sticker=random_sticker)
    # Иначе
    else:
        # уведомление пользователя о том, что ответа нет
        await bot.send_message(chat_id=message.chat.id,
                               text=message_templates[user_locale]['no answer'])


# Получение списка всех возможных типов входящих событий
all_types = list(types.ContentTypes.all())
# Исключение из списка стикера
all_types.remove('sticker')


@dp.message_handler(commands=['start', 'help'])
# Обрабатывает текстовые сообщения с командами start и help
async def start(message: types.Message):
    # Текст для сообщения
    start_text = message_templates[user_locale]['start']
    # Отправка сообщения
    await bot.send_message(chat_id=message.chat.id, text=start_text)


@dp.message_handler(content_types=all_types)
# Обрабатывает все входящие события, кроме стикеров и команд start и help
async def answer_to_text(message: types.Message):
    # Уведомление пользователя
    await message.reply(text=message_templates[user_locale]['message is not sticker'])
    # Получение рандомного стикера peace
    peace_stick = random.choice(stickers['✌️'])
    # Отправка стикера
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker=peace_stick)


# Запуск бота
executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)


# TODO: add language change on user locale definition 
# TODO: or add language manual change 