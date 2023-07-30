import sqlite3, os, random
import emoji
from aiogram import types
from functools import partial

from log import db_logger
from .tablenames import stickers_tablename, db_name


""" Database create, update and select """


def gather_sticker_data(sticker: types.Sticker) -> tuple[str, str, str]:
    """Unpacks sticker data.

    Args:
        sticker (types.Sticker): sticker to unpack.

    Returns:
        tuple: (sticker id, sticker emoji code, sticker set name)
    """
    stick_id = sticker.file_id  # file id of the sticker 
    stick_code = emoji.demojize(sticker.emoji)  # emoji code decoded, f.e. ":smiling face:"
    stick_set = sticker.set_name  # set name, which sticker belongs to
    return (stick_id, stick_code, stick_set)


def create_stickers_table(tablename: str = stickers_tablename, db_filename: os.PathLike = db_name) -> None:
    """Creates SQLite3 table, if it doesn't exist.

    Args:
        tablename (str, optional): name of the table in db. Defaults to stickers_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection 
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Create table 
    db_cursor.execute(f'CREATE TABLE IF NOT EXISTS {tablename} (file_id TEXT PRIMARY KEY, emoji TEXT NOT NULL, setname TEXT NOT NULL);')
    db_logger.info(f'Table {tablename} is setup')
    # Save changes 
    db_connection.commit()
    # Close the connection
    db_connection.close()


def check_sticker(sticker: types.Sticker, db_filename: os.PathLike = db_name, 
                  tablename: str = stickers_tablename) -> None:
    """Checks if sticker with the same file id is in db.

    Args:
        sticker (types.Sticker): sticker to check.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
        tablename (str, optional): name of the table in db. Defaults to stickers_tablename.

    Returns:
        bool: True, if it's not.
    """
    # Get sticker's data
    received_emoji_id, received_emoji_code, received_emoji_set = gather_sticker_data(sticker)   
    # Establish connection
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    # Select matching data
    query_text = f'SELECT * FROM {tablename} WHERE file_id="{received_emoji_id}" OR (setname="{received_emoji_set}" AND emoji="{received_emoji_code}");'
    same_in_db = cursor.execute(query_text).fetchone()
    # Close the connection
    connection.close()
    # Return matching status 
    return same_in_db is None


def add_sticker(sticker: types.Sticker, db_filename: os.PathLike = db_name, 
                tablename: str = stickers_tablename) -> None:
    """Adds sticker to db. 

    Args:
        sticker (types.Sticker): sticker to add.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
        tablename (str, optional): name of the table in db. Defaults to stickers_tablename.
    """
    # Gather sticker's data
    received_emoji_id, received_emoji_code, received_emoji_set = gather_sticker_data(sticker)
    # Establish the connection
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    # Add new data and save changes 
    cursor.execute(f'INSERT INTO {tablename} VALUES ("{received_emoji_id}", "{received_emoji_code}", "{received_emoji_set}");')
    db_logger.info(f'New sticker from {received_emoji_set} for emoji "{received_emoji_code}" saved')
    connection.commit()
    # Close the connection
    connection.close()


def add_set(*stickers: list) -> None:
    """Adds a set of stickers to db. 

    Args:
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
        *stickers (list): list of stickers to add. 
    """
    global db_name
    for sticker in stickers:
        if check_sticker(sticker=sticker, db_filename=db_name):
            add_sticker(sticker=sticker, db_filename=db_name)
        else:
            continue


def select_reply(sticker_to_reply: types.Sticker, tablename: str = stickers_tablename, anything: bool = False, db_filename: os.PathLike = db_name) -> str | None:
    """Selects random sticker as a reply. 
    
    Args: 
        sticker_to_reply (types.Sticker): sticker, which alternative must be found. 
        tablename (str, optional): table name in db. Defaults to stickers_tablename.
        anything (bool): find any sticker, or only suitable. Defaults to False.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    Returns:
        (str | None): id of sticker to reply with, if found.   
    """
    # Establish connection
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    # Define filters 
    target_emoji = emoji.demojize(sticker_to_reply.emoji)
    except_set = sticker_to_reply.set_name
    # Apply all the filters and perform search
    if anything == False:
        possible_answers = cursor.execute(f'SELECT file_id FROM {tablename} WHERE emoji = "{target_emoji}" AND NOT setname="{except_set}"').fetchall()
    else:
        possible_answers = cursor.execute(f'SELECT file_id FROM {tablename}').fetchall()    
    # Close the connection
    connection.close()
    
    # Return result 
    try: 
        answer = random.choice(possible_answers)
        return answer[0]
    except IndexError:  # if nothing is found 
        return None
    
    
""" Statistics """

def count_unique(value: str, tablename: str = stickers_tablename, db_filename: os.PathLike = db_name) -> int:
    """Counts unique values in the column of the table

    Args:
        value (str): column name in the table to analyze.
        tablename (str, optional): table to analyze. Defaults to stickers_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Returns:
        int: number of unique items.
    """
    # Establish connection
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    # Perform select
    selected_items = cursor.execute(f'SELECT {value} FROM {tablename}').fetchall()
    # Close the connection
    connection.close()
    # Count unique sets
    unique_num = len(set(selected_items))
    
    return unique_num


count_sets = partial(count_unique, value='setname')
count_emoji = partial(count_unique, value='emoji')