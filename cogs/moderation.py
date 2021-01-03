"""moderation cog"""

import discord
from discord.ext import commands

from useful_commands import is_moder, create_loop

con = create_loop()


class BotChange(commands.Cog):
    """
    commands with changes of bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_moder()
    async def change_prefix(self, ctx, prefix="."):
        """
        changes bot prefix

        :param ctx: context
        :type ctx: commands.Context
        :param prefix: prefix to change
        :type prefix: str
        """
        old_prefix = await con.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        await con.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2;", prefix, ctx.guild.id)
        emb = discord.Embed(color=0x2ecc71)
        emb.title = "Обновление!!!"
        emb.add_field(name="Новый префикс!", value="Префикс успешно изменен с {} на {}".format(old_prefix, prefix))
        emb.set_footer(text="Пример команды: {}help".format(prefix))
        await ctx.send(embed=emb)

    @commands.command()
    @is_moder()
    async def goodbye(self, ctx, text):
        """
        set goodbye text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new goodbye text
        :type text: str
        """
        await con.execute(
            "UPDATE guilds SET goodbye = $1 WHERE guild_id = $2;", text, ctx.guild.id)
        await ctx.send("Прощание успешно изменено.")

    @commands.command()
    @is_moder()
    async def welcome(self, ctx, text):
        """
        set welcome text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new welcome text
        :type text: str
        """
        await con.execute(
            "UPDATE guilds SET welcome = $1 WHERE guild_id = $2;", text, ctx.guild.id)
        await ctx.send("Приветствие успешно изменено.")


class UserChange(commands.Cog):
    """
    commands for users change
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_moder()
    async def give(self, ctx, member: discord.Member, money):
        """

        :param ctx: context
        :type ctx: commands.Context
        :param member: member to give him some money
        :type member: discord.Member
        :param money: money to give
        :type money: int
        """
        money = int(money)
        await con.execute("UPDATE users SET money = money+$1 WHERE user_id = $2 AND guild_id = $3;", money,
                          member.id,
                          ctx.guild.id)
        await ctx.send("{} вам выдано {} монет".format(member.mention, money))


def setup(bot):
    """
    setups bot

    :param bot: bot to setup
    :type bot: commands.Bot
    """
    bot.add_cog(BotChange(bot))
    bot.add_cog(UserChange(bot))
    print("Moderation finished")
