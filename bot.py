import random
import os, dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import sqlite3
import emoji


# Read the token from .env file 
# IMPORTANT: never share the token, otherwise the bot can be stollen. 
dotenv.load_dotenv()
token = os.getenv('DEMO_TOKEN')

# Create bot and dispatcher 
bot = Bot(token)
dp = Dispatcher(bot=bot)


def check_table(tablename: str = 'stickers', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    """Creates SQLite3 table, if it doesn't exist.

    Args:
        tablename (str, optional): name of the table in db. Defaults to 'stickers'.
        db_filename (os.PathLike, optional): path to db file. Defaults to os.environ.get('DB_NAME').
    """
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'CREATE TABLE IF NOT EXISTS {tablename} (file_id TEXT PRIMARY KEY, emoji TEXT NOT NULL, setname TEXT NOT NULL);')
    db_connection.commit()
    db_connection.close()


def check_sticker(sticker: types.Sticker, db_filename: os.PathLike = os.environ.get('DB_NAME')):
    """Checks if sticker with the same file id is in db.

    Args:
        sticker (types.Sticker): sticker to check.
        db_filename (os.PathLike, optional): path to db file. Defaults to os.environ.get('DB_NAME').

    Returns:
        bool: True, if it's not.
    """
    received_emoji_id = sticker.file_id
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    same_in_db = cursor.execute(f'SELECT * FROM stickers WHERE file_id="{received_emoji_id}";').fetchone()
    connection.close()
    return same_in_db is None


def add_sticker(sticker: types.Sticker, db_filename: os.PathLike = os.environ.get('DB_NAME')):
    """Adds sticker to db. 

    Args:
        sticker (types.Sticker): sticker to add.
        db_filename (os.PathLike, optional): path to db file. Defaults to os.environ.get('DB_NAME').
    """
    received_emoji_id = sticker.file_id
    received_emoji_code = emoji.demojize(sticker.emoji)
    received_emoji_set = sticker.set_name
    
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    cursor.execute(f'INSERT INTO stickers VALUES ("{received_emoji_id}", "{received_emoji_code}", "{received_emoji_set}");')
    connection.commit()
    connection.close()


def add_set(*stickers: list):
    """Adds a set of stickers to db. 

    Args:
        db_filename (os.PathLike, optional): path to db file. Defaults to os.environ.get('DB_NAME').
        *stickers (list): list of stickers to add. 
    """
    for sticker in stickers:
        if check_sticker(sticker=sticker, db_filename=os.environ.get('DB_NAME')):
            add_sticker(sticker=sticker, db_filename=os.environ.get('DB_NAME'))
        else:
            continue


def select_reply(sticker_to_reply: types.Sticker, tablename: str = 'stickers', anything: bool = False, db_filename: os.PathLike = os.environ.get('DB_NAME')) -> str | None:
    """Selects random sticker as a reply. 
    
    Args: 
        sticker_to_reply (types.Sticker): sticker, which alternative must be found. 
        tablename (str, optional): table name in db. Defaults to 'stickers'.
        anything (bool): find any sticker, or only suitable. Defaults to False.
        db_filename (os.PathLike, optional): path to db file. Defaults to os.environ.get('DB_NAME').
    Returns:
        (str | None): id of sticker to reply with, if found.   
    """
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    
    target_emoji = emoji.demojize(sticker_to_reply.emoji)
    except_set = sticker_to_reply.set_name
    if anything == False:
        possible_answers = cursor.execute(f'SELECT file_id FROM {tablename} WHERE emoji = "{target_emoji}" AND NOT setname="{except_set}"').fetchall()
    else:
        possible_answers = cursor.execute(f'SELECT file_id FROM {tablename}').fetchall()    
    connection.close()
    
    try: 
        answer = random.choice(possible_answers)
        return answer[0]
    except IndexError:
        return None

""" Bot functional starts here """

async def startup(_):
    check_table()


@dp.message_handler(content_types=['sticker'])
async def echo_sticker(message: types.Message):
    
    received_sticker = message.sticker       
    received_set = await bot.get_sticker_set(name=received_sticker.set_name)
    stickers_to_add = received_set.stickers
    add_set(*stickers_to_add)
    chosen_answer = select_reply(sticker_to_reply=received_sticker)
    
    if chosen_answer is None:
        chosen_answer = select_reply(sticker_to_reply=received_sticker, anything=True)
        await bot.send_message(chat_id=message.chat.id, text='Idk')
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
    else:
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
 
    
if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)