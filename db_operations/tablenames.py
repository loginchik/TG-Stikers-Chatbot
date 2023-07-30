"""
File contains the functions that are working with the database.
"""

import os, dotenv

dotenv.load_dotenv()

stickers_tablename = 'stickers'
users_statistics_tablename = 'users_stats'
daily_statistics_tablename = 'daily_stats'

db_name = os.environ.get('DB_NAME', default='data/database.db')
