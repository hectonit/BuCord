"""main file to start bot"""
import dbl
from discord.ext import commands

from constraints import BOT_TOKEN, DBL_TOKEN
from useful_commands import create_loop

con = create_loop()


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
        prefix = await con.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1", guild.id)
        return prefix


bot = commands.Bot(command_prefix=dynamic_prefix)
bot.remove_command("help")
bot.load_extension("cogs.general")
bot.load_extension("cogs.economy")
bot.load_extension("cogs.moderation")
dbl_py = dbl.DBLClient(bot, DBL_TOKEN, autopost=True)
bot.run(str(BOT_TOKEN))
