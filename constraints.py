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
colors = [0x9b59b6, 0x1abc9c, 0x2ecc71, 0x3498db,
          0x34495e, 0x16a085, 0x27ae60, 0x2980b9, 0x8e44ad, 0x2c3e50,
          0xf1c40f, 0xe67e22, 0xe74c3c, 0xecf0f1,
          0x95a5a6, 0xf39c12, 0xd35400, 0xc0392b, 0xbdc3c7, 0x7f8c8d
          ]
commands_descriptions = {
    "help": {
        "info": "выводит справку по командам",
        "use": "{}help [команда или секция]",
    },
    "dollar": {
        "info": "выводит курс доллара к рублю",
        "use": "{}dollar",
    },
    "balance": {
        "info": "выводит баланс участника",
        "use": "{}balance [участник сервера]",
    },
    "give": {
        "info": "добавляет участнику указанное кол-во монет(только для модераторов)",
        "use": "{}give <учатсник сервера> <монеты>",
    },
    "mine_info": {
        "info": "выводит кол-во намайненых монет участника",
        "use": "{}mine_info [участник сервера]",
    },
    "withdrawal": {
        "info": "выводит монеты с майнинга на баланс",
        "use": "{}withdrawal <монеты>",
    },
    "bet": {
        "info": "вы ставите монеты(принцип как в казино)",
        "use": "{}bet <монеты>",
    },
    "top": {
        "info": "выводит топ участников по монетам",
        "use": "{}top",
    },
    "user_card": {
        "info": "выводит карточку участника",
        "use": "{}user_card [участник сервера]",
    },
    "goodbye": {
        "info": "настраивает прощание",
        "use": "{}goodbye <текст , символами {} обозначьте участника>",
    },
    "welcome": {
        "info": "настраивает приветствие",
        "use": "{}welcome <текст , символами {} обозначьте участника>",
    },
    "find_bug": {
        "info": "отправляет разработчикам информацию о баге",
        "use": "{}find_bug \"<краткое описание бага>\" \"<полное описание бага>\" [url-адрес картинки]",
    },
    "bot_info": {
        "info": "выводит информацию о боте",
        "use": "{}bot_info",
    },
    "ping": {
        "info": "выводит пинг бота",
        "use": "{}ping",
    },
    "change_prefix": {
        "info": "изменяет префикс бота",
        "use": "{}change_prefix [префикс]",
    }
}
