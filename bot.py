import random

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor, exceptions
from bs4 import BeautifulSoup

# Импорт токена из файла с токеном
with open('token.txt') as token_file:
    token = token_file.read()

# Создание бота и диспетчера
bot = Bot(token)
dp = Dispatcher(bot=bot)

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

    # Определение пользовательского стикера
    user_sticker = message.sticker
    # Определение стикерпака, в котором пользовательский стикер
    set_name = user_sticker.set_name

    # Если этот стикерпак возможно сохранить в программу
    if set_name != 'None':
        # Получение списка всех используемых в программе стикерпаков
        sets = get_used_sets()
        # Если этого стикера нет
        if set_name not in sets:
            # Уведомление пользователя
            await bot.send_message(chat_id=message.chat.id,
                                   text='Минуту, я сохраню этот пак себе...\n'
                                        'Пришлю стикер в ответ, когда закончу')
            # Запись стикерпака в список для программы
            write_new_set(set_name)
            # Перезагрузка словаря со стикерами, чтобы включить туда новый пак
            await download_stickers_to_use()

    # Определение эмоджи, соответствующего пользовательскому стикеру
    user_emoji = user_sticker.emoji

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
                               text='Тут и сказать нечего')


# Получение списка всех возможных типов входящих событий
all_types = list(types.ContentTypes.all())
# Исключение из списка стикера
all_types.remove('sticker')


@dp.message_handler(commands=['start', 'help'])
# Обрабатывает текстовые сообщения с командами start и help
async def start(message: types.Message):
    # Текст для сообщения
    start_text = '18+\nОтправь стикер – пришлю такой же по эмоджи'
    # Отправка сообщения
    await bot.send_message(chat_id=message.chat.id, text=start_text)


@dp.message_handler(content_types=all_types)
# Обрабатывает все входящие события, кроме стикеров и команд start и help
async def answer_to_text(message: types.Message):
    # Уведомление пользователя
    await message.reply(text='Я не умею общаться не стикерами, сорри')
    # Получение рандомного стикера peace
    peace_stick = random.choice(stickers['✌️'])
    # Отправка стикера
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker=peace_stick)


# Запуск бота
executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)
