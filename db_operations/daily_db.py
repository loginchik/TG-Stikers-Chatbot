""" Daily activity stats """
import sqlite3, os

from functools import partial

from log import db_logger
from .date_func import todays_date
from .tablenames import daily_statistics_tablename, db_name


def create_dailystats_table(tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Creates daily statistics table, if it does not exist.

    Args:
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Create table 
    
    query_text = f'''CREATE TABLE IF NOT EXISTS {tablename}
                      (dayID INTEGER PRIMARY KEY AUTOINCREMENT,
                      day DATE NOT NULL, 
                      commands_use INT DEFAULT 0, 
                      stickers_send INT DEFAULT 0, 
                      other_messages INT DEFAULT 0);'''
    db_cursor.execute(query_text)
    db_logger.info(f'Table {tablename} is setup')
    # Save changes 
    db_connection.commit()
    # Close the connection
    db_connection.close()


def check_daily_record_exists(day: str = todays_date(), tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> bool:
    """Check if there is a record of today's date.

    Args:
        day (str, optional): date to check. Defaults to todays_date().
        tablename (str, optional): table name to look in. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Raises:
        KeyError: in case there are several records for the date

    Returns:
        bool: True, if exists, False, if doesn't. 
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    result = db_cursor.execute(f'''SELECT * FROM {tablename} WHERE day="{day}";''').fetchall()
    # Close the connection
    db_connection.close()
    
    if len(result) == 0:
        return False
    elif len(result) == 1:
        return True
    else:
        raise KeyError('There are more than 1 daily records')
 
    
def get_daily_value(day: str, column_name: str, tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets a value of specified column from the day record. 

    Args:
        day (str): string of the date.
        column_name (str): name of the column.
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.

    Returns:
        _type_: _description_
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    value = db_cursor.execute(f'''SELECT {column_name} FROM {tablename} WHERE day="{day}"''').fetchone()
    # Close the connection
    db_connection.close()
    # Return value
    return value[0]


get_commands_use = partial(get_daily_value, column_name='commands_use')
get_stickers_send = partial(get_daily_value, column_name='stickers_send')
get_other_messages = partial(get_daily_value, column_name='other_messages')


def update_daily_value(day: str, column_name: str, new_value: int, tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Updates specified record and column.

    Args:
        day (str): day of the record.
        column_name (str): column name to update value.
        new_value (int): new value to write.
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    db_cursor.execute(f'''UPDATE {tablename} SET {column_name}={new_value} WHERE day="{day}"''')
    db_connection.commit()
    # Close the connection
    db_connection.close()

   
update_commands_use = partial(update_daily_value, column_name='commands_use')
update_stickers_send = partial(update_daily_value, column_name='stickers_send')
update_other_messages = partial(update_daily_value, column_name='other_messages')

    
def add_daily_record(day: str = todays_date(), tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Creates new row of the day, so called daily record. 

    Args:
        day (str, optional): this day in string format. Defaults to todays_date().
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    this_day = todays_date()
    
    # Get value
    query_text = f'''INSERT INTO {tablename} (day) VALUES ("{this_day}")'''
    db_cursor.execute(query_text)
    db_connection.commit()
    
    # Close the connection
    db_connection.close()


def add_stickers_send(day: str = todays_date(), tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of stickers, sent today, and writes current + 1

    Args:
        day (str, optional): this day. Defaults to todays_date().
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_stickers_send(day=day, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_stickers_send(day=day, new_value=new_value, tablename=tablename, db_filename=db_filename)


def add_commands_use(day: str = todays_date(), tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of used commands, received today, and writes current + 1

    Args:
        day (str, optional): this day. Defaults to todays_date().
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_commands_use(day=day, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_commands_use(day=day, new_value=new_value, tablename=tablename, db_filename=db_filename)


def add_other_messages(day: str = todays_date(), tablename: str = daily_statistics_tablename, db_filename: os.PathLike = db_name) -> None:
    """Gets current value of other messages, received today, and writes current + 1

    Args:
        day (str, optional): this day. Defaults to todays_date().
        tablename (str, optional): name of the table. Defaults to daily_statistics_tablename.
        db_filename (os.PathLike, optional): path to db file. Defaults to db_name.
    """
    current_value = get_other_messages(day=day, tablename=tablename, db_filename=db_filename)
    new_value = current_value + 1
    update_other_messages(day=day, new_value=new_value, tablename=tablename, db_filename=db_filename)