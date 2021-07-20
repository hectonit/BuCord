"""main file to start bot"""

import dbl
import discord
from discord.ext import commands

from constraints import BOT_TOKEN, DBL_TOKEN
from useful_commands import connect

con = connect()


async def dynamic_prefix(pref_bot, message):
    """
    function for dynamic prefix for bot

    :param pref_bot: discord bot
    :type pref_bot: commands.Bot
    :param message: each message
    :type message: discord.Message
    :return: prefix
    :rtype: str
    """
    guild = message.guild
    if guild is None:
        return await pref_bot.get_prefix(message)
    else:
        with con.cursor() as cur:
            prefix = cur.fetch_val("SELECT prefix FROM guilds WHERE guild_id = %s", guild.id)
        return commands.when_mentioned_or(prefix)(pref_bot, message)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=dynamic_prefix, intents=intents)
bot.remove_command("help")
bot.load_extension("cogs.general")
bot.load_extension("cogs.economy")
bot.load_extension("cogs.moderation")
bot.load_extension("cogs.games")
dbl_py = dbl.DBLClient(bot, DBL_TOKEN, autopost=True)
bot.run(str(BOT_TOKEN))
