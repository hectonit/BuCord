"""module for important constraints"""
import os

try:
    from . import configs
except ImportError:
    DBL_TOKEN = os.environ.get("DBL_TOKEN")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_PASS = os.environ.get("REDIS_PASS")
else:
    DBL_TOKEN = configs.dbltoken
    DATABASE_URL = configs.database
    BOT_TOKEN = configs.token
    REDIS_HOST = configs.redis_host
    REDIS_PORT = configs.redis_port
    REDIS_PASS = configs.redis_pass

ONE_DAY = 86400

MAX_MEMBERS = 1000

MY_ID = 530751275663491092

table = "+---+---+---+\n| 1 | 2 | 3 |\n+---+---+---+\n| 4 | 5 | 6 |\n+---+---+---+\n| 7 | 8 | 9 |\n+---+---+---+"

commands_descriptions = {
    "help": {
        "info": "выводит справку по командам",
        "use": "help [команда или секция]",
    },
    "exchange_rate": {
        "info": "выводит курс какой-либо валюты (доллар по умолчанию) к какой-либо валюте",
        "use": "course [обозначение первой валюты] [обозначение второй валюты]",
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
        "use": "goodbye <текст>",
    },
    "welcome": {
        "info": "настраивает приветствие",
        "use": "welcome <текст>",
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
    },
    "tictactoe": {
        "info": "известная игра крестики-нолики",
        "use": "tictactoe [уровень сложности `easy`, `medium` или `hard`, по умолчанию medium]",
    }
}
