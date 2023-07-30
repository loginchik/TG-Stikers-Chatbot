import os, json
import dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from log import activity_logger
from db_operations import daily_db, stickers_db, users_db


# Read the token from .env file 
# IMPORTANT: never share the token, otherwise the bot can be stollen. 
dotenv.load_dotenv()
token = os.getenv('DEMO_TOKEN')

# Create bot and dispatcher 
bot = Bot(token)
dp = Dispatcher(bot=bot)

# Define default user locale
user_locale_global = 'en'

# Read message templates data
with open('data/message_templates.json') as templates_file:
    message_templates = json.load(templates_file)
    

async def startup(_):
    # Check tables exsit on startup
    daily_db.create_dailystats_table()
    stickers_db.create_stickers_table()
    users_db.create_userstats_table()
    
    if not daily_db.check_daily_record_exists():
        daily_db.add_daily_record()


def update_user_locale(message: types.Message) -> str:
    """Func gets message to define user locale and current locale status. 
    Depending on the results, returns either user locale, or 'en'.

    Args:
        message (types.Message): message from user. 

    Returns:
        str: new locale. 
    """
    global message_templates
    global user_locale_global
    
    current_locale = user_locale_global
    
    possible_locales = list(message_templates.keys())
    if message.from_user.locale != current_locale:
        user_locale = message.from_user.locale
        if user_locale in possible_locales:
            return user_locale
        else:
            return 'en'
    else:
        return current_locale


# Handles incoming stickers
@dp.message_handler(content_types=['sticker'])
async def echo_sticker(message: types.Message):
    """Accepts message with a sticker and sends some sticker in return 

    Args:
        message (types.Message): message from user. 
    """
    global user_locale_global
    
    # Gather received sticker
    received_sticker = message.sticker     
    # Define it's set  
    received_set = await bot.get_sticker_set(name=received_sticker.set_name)
    # Add set to db, if necessary
    stickers_db.add_set(*received_set.stickers)
    # Choose sticker in return 
    chosen_answer = stickers_db.select_reply(sticker_to_reply=received_sticker)
    
    # If return sticker was not found
    # which means that other packages do not have a sticker with such emoji
    if chosen_answer is None:
        # then any sticker is chosen
        chosen_answer = stickers_db.select_reply(sticker_to_reply=received_sticker, anything=True)
        # and send to user with a notification
        user_locale_global = update_user_locale(message=message, current_locale=user_locale_global)
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale_global]['no answer'])
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent random sticker in return, as suitable was not found')
    # Though, if sticker in return is found, then it is send to user
    else:
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent sticker in return')
    
    # Update DB stats 
    users_db.update_last_usage(user_id=message.from_user.id)
    users_db.add_sticker_send(user_id=message.from_user.id)
    daily_db.add_stickers_send()

 
# Handles commands
@dp.message_handler(commands=['start', 'help', 'stats'])
async def define_command(message: types.Message):
    global user_locale_global
    
    this_command = message.get_command()
    
    # Start command sends start text
    if this_command == '/start':
        
        # Add user, if they aren't in db already
        if not users_db.user_exists(user_id=message.from_user.id):
            users_db.add_user_on_start(user_id=message.from_user.id)
        user_locale_global = update_user_locale(message=message)
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale_global]['start'])
        activity_logger.info('Command - /start')
    # Help command sends help text
    elif this_command == '/help':      
        user_locale_global = update_user_locale(message=message)  
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale_global]['help'])
        activity_logger.info('Command - /help')
    # Staats command counts statistics and sends it
    elif this_command == '/stats':
        sets_num = stickers_db.count_sets()
        emoji_num = stickers_db.count_emoji()
        user_locale_global = update_user_locale(message=message)
        stats_text = message_templates[user_locale_global]['stats'].format(sets_num, emoji_num)
        await bot.send_message(chat_id=message.chat.id, text=stats_text)
        activity_logger.info('Command - /stats')
    
    # Update DB stats 
    users_db.update_last_usage(user_id=message.from_user.id)
    users_db.add_command_use(user_id=message.from_user.id)
    daily_db.add_commands_use()

        
# Handles all other messages
@dp.message_handler()
async def unknown_message(message: types.Message):  
    global user_locale_global  
    # Send notification to user 
    user_locale_global = update_user_locale(message=message)
    await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale_global]['message is not sticker'])
    activity_logger.info('Message is nor sticker, neither command')
    
    # Update DB stats
    users_db.update_last_usage(user_id=message.from_user.id)
    users_db.add_other_message(user_id=message.from_user.id)
    daily_db.add_other_messages()

    
if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)