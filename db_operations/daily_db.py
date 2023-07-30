""" Daily activity stats """
import sqlite3, os
import dotenv

from functools import partial

from log import db_logger
from date_func import todays_date

dotenv.load_dotenv()


def check_daily_stats_table(tablename: str = 'daily_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Create table 
    db_cursor.execute(f'''CREATE TABLE IF NOT EXISTS {tablename} 
                      (day DATE PRIMARY KEY, 
                      commands_use INT DEFAULT 0, 
                      stickers_send_to INT DEFAULT 0, 
                      other_messages INT DEFAULT 0);''')
    db_logger.info(f'Table {tablename} is setup')
    # Save changes 
    db_connection.commit()
    # Close the connection
    db_connection.close()
    
def get_daily_value(day: str, column_name: str, tablename: str = 'daily_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    value = db_cursor.execute(f'''SELECT {column_name} FROM {tablename} WHERE day={day}''').fetchone()
    # Close the connection
    db_connection.close()
    # Return value
    return value[0]

def update_daily_value(day: str, column_name: str, new_value: int, tablename: str = 'daily_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    db_cursor.execute(f'''UPDATE {tablename} SET {column_name}={new_value} WHERE day={day}''')
    db_connection.commit()
    # Close the connection
    db_connection.close()
    
def add_daily_record(day: str = todays_date(), tablename: str = 'daily_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    db_cursor.execute(f'''INSERT INTO {tablename} (day) VALUES ({day})''')
    db_connection.commit()
    # Close the connection
    db_connection.close()
    
def check_daily_record_exists(day: str = todays_date(), tablename: str = 'daily_stats', db_filename: os.PathLike = os.environ.get('DB_NAME')):
    # Establish connection
    db_connection = sqlite3.connect(db_filename)
    db_cursor = db_connection.cursor()
    # Get value
    result = db_cursor.execute(f'''SELECT * FROM {tablename} WHERE day={day};''').fetchall()
    # Close the connection
    db_connection.close()
    
    if len(result) == 0:
        return False
    elif len(result) == 1:
        return True
    else:
        raise KeyError('There are more than 1 daily records')