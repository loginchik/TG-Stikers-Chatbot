"""User activity stats"""

import sqlite3, os
from functools import partial

from log import db_logger
from .date_func import todays_date
from .tablenames import users_statistics_tablename, db_name


def create_userstats_table(tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name):
    """Creates user statistics table, if it doesn't exists.

    Args:
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Create table 
    db_cursor.execute(f'''CREATE TABLE IF NOT EXISTS {tablename} 
                      (user_id INT PRIMARY KEY, 
                      first_usage DATE, 
                      last_usage DATE, 
                      commands_use INT DEFAULT 0, 
                      stickers_send_to INT DEFAULT 0, 
                      other_messages INT DEFAULT 0);''')
    # Save changes 
    db_connection.commit()
    # Close the connection
    db_connection.close()
    
    db_logger.info(f'USERS DB. Table {tablename} is setup')

    
def add_user_on_start(user_id: int, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name):
    """Adds a row of user to table and sets both first and last usages to today's date. 

    Args:
        user_id (int): user ID from TG.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Add a record
    db_cursor.execute(f'''INSERT INTO {tablename} (user_id, first_usage, last_usage)
                      VALUES ({user_id}, "{todays_date()}", "{todays_date()}")''')
    db_connection.commit()
    # Close connection 
    db_connection.close()
    
    db_logger.info(f'USERS DB. User creation')
    

def user_exists(user_id: int, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> bool:
    """Checks if user exists in the table (if there is the same ID). 

    Args:
        user_id (int): user TG ID.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Returns:
        bool: True, if exists. 
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Add a record
    result = db_cursor.execute(f'''SELECT * FROM {tablename} WHERE user_id={user_id}''').fetchall()
    # Close connection 
    db_connection.close()
    # Generate result
    if len(result) == 1:
        return True
    elif len(result) == 0:
        return False
    else:
        db_logger.error(f'More than one user with the ID of {user_id} in DB found')
        return True

    
def update_user_record(user_id: int, column_name: str, new_value: int | str, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Changes user record data in db.

    Args:
        user_id (int): user TG ID.
        column_name (str): name of the column to change.
        new_value (int | str): new value to write. 
        tablename (str, optional): name or the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Update the data
    if type(new_value) == str:
        new_value = f'"{new_value}"'
    db_cursor.execute(f'''UPDATE {tablename} SET {column_name}={new_value} WHERE user_id={user_id};''')
    db_connection.commit()
    
    # Close connection 
    db_connection.close()
    
    db_logger.info(f'USERS DB. User record update: {column_name} is set to {new_value}')


update_last_usage = partial(update_user_record, column_name='last_usage', new_value=todays_date())
update_commands_count = partial(update_user_record, column_name='commands_use')
update_stickers_count = partial(update_user_record, column_name='stickers_send_to')
update_other_messages_count = partial(update_user_record, column_name='other_messages')


def get_user_value(user_id: int, column_name: str, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> int | str:
    """Gets a specified column value from user record. 

    Args:
        user_id (int): user TG ID.
        column_name (str): name of the column. 
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Returns:
        int | str: current value of the specified column.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Update the data
    result = db_cursor.execute(f'''SELECT {column_name} FROM {tablename} WHERE user_id={user_id};''').fetchone()
    
    # Close connection 
    db_connection.close()
    
    return result[0]


get_current_commands_count = partial(get_user_value, column_name='commands_use')
get_current_stickers_count = partial(get_user_value, column_name='stickers_send_to')
get_current_other_messages_count = partial(get_user_value, column_name='other_messages')


def add_command_use(user_id: int, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of used commands, received from user, and writes current + 1

    Args:
        user_id (int): user TG ID.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_current_commands_count(user_id=user_id, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_commands_count(user_id=user_id, new_value=new_value, tablename=tablename, db_filename=db_filename)


def add_sticker_send(user_id: int, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of stickers, sent to user, and writes current + 1

    Args:
        user_id (int): user TG ID.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_current_stickers_count(user_id=user_id, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_stickers_count(user_id=user_id, new_value=new_value, tablename=tablename, db_filename=db_filename)


def add_other_message(user_id: int, tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of other messages, received from user, and writes current + 1

    Args:
        user_id (int): user TG ID.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_current_other_messages_count(user_id=user_id, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_other_messages_count(user_id=user_id, new_value=new_value, tablename=tablename, db_filename=db_filename)
    
    
    """ Statistics """
    
def count_users(tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> int:
    """Counts users that are in the db. 
    As all the rows are unique, is it enough to count the rows.

    Args:
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Returns:
        int: number of users. 
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Gather data 
    users = db_cursor.execute(f'''SELECT * FROM {tablename}''').fetchall()
    
    # Close connection 
    db_connection.close()
    
    return len(users)
    
    
def count_stickers(column_name: str = 'stickers_send_to', tablename: str = users_statistics_tablename, db_filename: os.PathLike = db_name) -> int:
    """Sums the values of 'stickers_send_to' column, or any other specified. 

    Args:
        column_name (str, optional): name of the column to sum. Defaults to 'stickers_send_to'.
        tablename (str, optional): name of the table. Defaults to users_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_filename.

    Returns:
        int: result. 
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Update the data
    result = db_cursor.execute(f'''SELECT SUM({column_name}) FROM {tablename}''').fetchone()
    
    # Close connection 
    db_connection.close()
    
    return result[0]