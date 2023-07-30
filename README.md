# TG Sticker Bot

Telegram bot that is written with aiogram. Saves stickers, sends stickers, spreads joy. 

* [How it works](#how-it-works)
    * [Chat actions](#chat-actions)
    * [Statistics](#statistics)
    * [User locale](#user-locale)
* [Project structure](#project-structure)

## How it works:

### Chat actions

Bot receives a sticker from user. Sticker object in TG has an atribute `set_name` — it defines a set name the sticker belongs to. Using the name, bot saves new sticker set to collection, if necessary. That is how updating the collection works. 

> See [stickers_db.py](db_operations/stickers_db.py) for code.

Another atribute is `emoji` assigned to a sticker. All the emoji are 'decoded' with `emoji` package (see [docs](https://pypi.org/project/emoji/)). Bot gets it and looks for collected stickers with the same emoji assigned but different sticker set in the collection.

If any stickers are found, bot chooses one of them and sends it to user in return. That is the target action of the bot. Though, if no matching stickers from other sets are found in the collection, bot notifies user and sends any random sticker as a sorry gesture. 

> See [stickers_db.py](db_operations/stickers_db.py) and [bot.py](bot.py) for code.

Bot can also interact with commands (start, help, stats, about). If any other message is received, bot notifies that it has no programmed reply. 

All the texts for messages that bot sends are collected into [message_templates.json](data/message_templates.json) and read at bot start up. 

### Statistics 

Activity is divided into 3 categories: commands interaction, stickers, other messages. These activities are counted in two ways: per day (date is key) and per user (user_id is the key). 

Every time bot receives a command, it adds 1 to commands interactions. Every time bot sends a sticker, it adds 1 to stickers interactions. Every time bot receives unknown message, it adds 1 to the category. 

Database update actions are logged into `db.log` file in [logs](logs/) folder. Bot start up, shut down, the facts of messages being sent are logged into `activity.log` file in [logs](logs/) folder. Unknown locales and emojies with no answer are logged into `improvements.log` in [logs](logs/) folder. 

### User locale

Bot switches to a language, that is set as user's locale. To make it possible, [message_templates.json](data/message_templates.json) has the structure of:

```json
{
    "locale": {
        "template_name": "template_text", 
        "template_name": "template_text"
        ...
    }, 
    "locale": {
        "template_name": "template_text", 
        "template_name": "template_text"
        ...
    }
    ...
}
```

Thus, every time bot has to send a message, text is extracted from the dictionary like this: `message_templates[user_locale][template_name]`.

> See [bot.py](bot.py) for examples.

### Daily report and scheduler

Bot has scheduler that runs two tasks: every midnight it adds a new row to daily statistics table. Every day at 23 hours scheduler makes bot send a report to admin. Admin ID is stored in environmental variables. 

## Project structure 

```
project 
├── data
│   ├── message_templates.json
│   └── database.db
├── db_operations
│   ├── __init.py__
│   ├── daily_db.py
│   ├── date_func.py
│   ├── stickers_db.py
│   ├── tablenames.py
│   └── users_db.py
├── logs
│   ├── activity.log
│   ├── db.log
│   ├── improvements.log
│   └── database.db
├── bot.py
├── make_report.py
├── LICENSE
├── README.md
└── requirements.txt
```

Database name is stored in environmental variables. Same is TG token from BotFather. 