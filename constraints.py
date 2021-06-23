"""module for important constraints"""
import os

try:
    import configs
except ModuleNotFoundError:
    DBL_TOKEN = os.environ.get("DBL_TOKEN")
    DATABASE_URL = os.environ.get('DATABASE_URL')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
else:
    DBL_TOKEN = configs.dbltoken
    DATABASE_URL = configs.database
    BOT_TOKEN = configs.token
MAX_MEMBERS = 10000
MY_ID = 530751275663491092
commands_descriptions = {
    "help": {
        "info": "выводит справку по командам",
        "use": "help [команда или секция]",
    },
    "course": {
        "info": "выводит курс какой-либо валюты (доллар по умолчанию) к рублю",
        "use": "course [обозначение валюты например: USD (доллар)]",
    },
    "balance": {
        "info": "выводит баланс участника",
        "use": "balance [участник сервера]",
    },
    "give": {
        "info": "добавляет участнику указанное кол-во монет(только для модераторов)",
        "use": "give <участник сервера> <монеты>",
    },
    "bet": {
        "info": "вы ставите монеты(принцип как в казино)",
        "use": "bet <монеты>",
    },
    "top": {
        "info": "выводит топ участников по монетам",
        "use": "top",
    },
    "user_card": {
        "info": "выводит карточку участника",
        "use": "user_card [участник сервера]",
    },
    "goodbye": {
        "info": "настраивает прощание",
        "use": "goodbye <текст , символами {} обозначьте участника>",
    },
    "welcome": {
        "info": "настраивает приветствие",
        "use": "welcome <текст , символами {} обозначьте участника>",
    },
    "find_bug": {
        "info": "отправляет разработчикам информацию о баге",
        "use": "find_bug \"<краткое описание бага>\" \"<полное описание бага>\" [url-адрес картинки]",
    },
    "bot_info": {
        "info": "выводит информацию о боте",
        "use": "bot_info",
    },
    "ping": {
        "info": "выводит пинг бота",
        "use": "ping",
    },
    "change_prefix": {
        "info": "изменяет префикс бота",
        "use": "change_prefix [префикс]",
    }
}
