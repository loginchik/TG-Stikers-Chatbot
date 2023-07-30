"""User activity stats"""

import sqlite3, os
from functools import partial

from log import db_logger
from date_func import todays_date


def check_statistics_table(tablename: str = 'user_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
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
    db_logger.info(f'Table {tablename} is setup')
    # Save changes 
    db_connection.commit()
    # Close the connection
    db_connection.close()

    
def add_user_on_start(user_id: int, tablename: str = 'user_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Add a record
    db_cursor.execute(f'''INSERT INTO {tablename} (user_id, first_usage, last_usage)
                      VALUES ({user_id}, {todays_date()}, {todays_date()})''')
    db_connection.commit()
    # Close connection 
    db_connection.close()
    

def user_exists(user_id: int, tablename: str = 'user_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Add a record
    result = db_cursor.execute(f'''SELECT * FROM {tablename} WHERE user_id={user_id}''').fetchall()
    # Close connection 
    db_connection.close()

    if len(result) == 1:
        return True
    elif len(result) == 0:
        return False
    else:
        raise KeyError('there are more than 1 records of the user')

    
def change_user_record(user_id: int, column_name: str, new_value: int | str, tablename: str = 'user_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
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

def get_user_record(user_id: int, column_name: str, tablename: str = 'user_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')) -> int | str:
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    
    # Update the data
    result = db_cursor.execute(f'''SELECT {column_name} FROM {tablename} WHERE user_id={user_id};''').fetchone()
    
    # Close connection 
    db_connection.close()
    
    return result[0]

get_current_commands_count = partial(get_user_record, column_name='commands_use')
get_current_stickers_send_to_count = partial(get_user_record, column_name='stickers_send_to')
get_current_other_messages_count = partial(get_user_record, column_name='other_messages')
    
change_last_usage = partial(change_user_record, column_name='last_usage', new_value=todays_date())

def update_commands_count(user_id):
    current_value = get_current_commands_count(user_id=user_id)
    new_value = current_value + 1 
    change_user_record(user_id=user_id, column_name='commands_use', new_value=new_value)
    
def update_stickers_count(user_id):
    current_value = get_current_stickers_send_to_count(user_id=user_id)
    new_value = current_value + 1 
    change_user_record(user_id=user_id, column_name='stickers_send_to', new_value=new_value)
    
def update_other_messages_count(user_id):
    current_value = get_current_other_messages_count(user_id=user_id)
    new_value = current_value + 1 
    change_user_record(user_id=user_id, column_name='other_messages', new_value=new_value)
    
