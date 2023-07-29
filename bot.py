import os, dotenv
import json

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from log import activity_logger
from db import check_table, add_set, select_reply


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


""" Bot functional starts here """

async def startup(_):
    check_table()


@dp.message_handler(content_types=['sticker'])
async def echo_sticker(message: types.Message):
    
    received_sticker = message.sticker       
    received_set = await bot.get_sticker_set(name=received_sticker.set_name)
    add_set(*received_set.stickers)
    chosen_answer = select_reply(sticker_to_reply=received_sticker)
    
    if chosen_answer is None:
        chosen_answer = select_reply(sticker_to_reply=received_sticker, anything=True)
        await bot.send_message(chat_id=message.chat.id, text=message_templates[user_locale]['no answer'])
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent random sticker in return, as suitable was not found')
    else:
        await bot.send_sticker(chat_id=message.chat.id, sticker=chosen_answer)
        activity_logger.info('Sent sticker in return')
 
    
if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=startup)