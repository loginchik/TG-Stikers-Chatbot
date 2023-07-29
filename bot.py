import os, json
import dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from log import activity_logger
from db import check_table, add_set, select_reply, count_unique


# Read the token from .env file 
# IMPORTANT: never share the token, otherwise the bot can be stollen. 
dotenv.load_dotenv()
token = os.getenv('DEMO_TOKEN')

# Create bot and dispatcher 
bot = Bot(token)
dp = Dispatcher(bot=bot)

# Define default user locale
user_locale = 'en'

# Read message templates data
with open('data/message_templates.json') as templates_file:
    message_templates = json.load(templates_file)
    

async def startup(_):
    # Check table exsits on startup
    check_table()

@dp.message_handler(content_types=['sticker'])
async def echo_sticker(message: types.Message):
    """Accepts message with a sticker and sends some sticker in return 

    Args:
        message (types.Message): message from user. 
    """
    # Gather received sticker
    received_sticker = message.sticker     
    # Define it's set  
    received_set = await bot.get_sticker_set(name=received_sticker.set_name)
    # Add set to db, if necessary
    add_set(*received_set.stickers)
    # Choose sticker in return 
    chosen_answer = select_reply(sticker_to_reply=received_sticker)
    
    # If return sticker was not found
    # which means that other packages do not have a sticker with such emoji
    if chosen_answer is None:
        # then any sticker is chosen
        chosen_answer = select_reply(sticker_to_reply=received_sticker, anything=True)
        # and send to user with a notification
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale]['no answer'])
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent random sticker in return, as suitable was not found')
    # Though, if sticker in return is found, then it is send to user
    else:
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent sticker in return')
 
@dp.message_handler(commands=['start', 'help', 'stats'])
async def define_command(message: types.Message):
    this_command = message.get_command()
    
    # Start command sends start text
    if this_command == '/start':
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale]['start'])
    # Help command sends help text
    elif this_command == '/help':
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale]['help'])
    # Staats command counts statistics and sends it
    elif this_command == '/stats':
        sets_num = count_unique(value='setname')
        emoji_num = count_unique(value='emoji')
        stats_text = message_templates[user_locale]['stats'].format(sets_num, emoji_num)
        await bot.send_message(chat_id=message.chat.id, text=stats_text)
        
    
    
 
    
if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)