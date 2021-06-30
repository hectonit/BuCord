"""moderation cog"""
import discord
from discord.ext import commands

from useful_commands import connect

con = connect()


class BotChange(commands.Cog):
    """
    commands with changes of bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix="."):
        """
        changes bot prefix

        :param ctx: context
        :type ctx: commands.Context
        :param prefix: prefix to change
        :type prefix: str
        """
        with con.cursor() as cur:
            old_prefix = cur.fetch_val("SELECT prefix FROM guilds WHERE guild_id = %s;", ctx.guild.id)
        try:
            prefix.encode("ascii")
        except UnicodeEncodeError:
            emb = discord.Embed(color=0xf55c47)
            emb.title = "Ошибка"
            emb.add_field(name="Префикс не изменен!", value="Префикс может содержать только ascii символы")
            emb.set_footer(text="Пример команды: {}help".format(old_prefix))
            await ctx.send(embed=emb)
            return
        if len(prefix) > 5:
            emb = discord.Embed(color=0xf55c47)
            emb.title = "Ошибка"
            emb.add_field(name="Префикс не изменен!", value="Длина префикса не может превышать 5 символов")
            emb.set_footer(text="Пример команды: {}help".format(old_prefix))
            await ctx.send(embed=emb)
            return
        with con.cursor() as cur:
            cur.execute("UPDATE guilds SET prefix = %s WHERE guild_id = %s;", prefix, ctx.guild.id)
        emb = discord.Embed(color=0x2ecc71)
        emb.title = "Обновление"
        emb.add_field(name="Новый префикс!", value="Префикс успешно изменен с {} на {}".format(old_prefix, prefix))
        emb.set_footer(text="Пример команды: {}help".format(prefix))
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def goodbye(self, ctx, *text):
        """
        set goodbye text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new goodbye text
        :type text: str
        """
        with con.cursor() as cur:
            cur.execute(
                "UPDATE guilds SET goodbye = %s WHERE guild_id = %s;", text, ctx.guild.id)
        await ctx.send("Прощание успешно изменено.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, *text):
        """
        set welcome text

        :param ctx: context
        :type ctx: commands.Context
        :param text: new welcome text
        :type text: str
        """
        with con.cursor() as cur:
            cur.execute(
                "UPDATE guilds SET welcome = %s WHERE guild_id = %s;", text, ctx.guild.id)
        await ctx.send("Приветствие успешно изменено.")


class UserChange(commands.Cog):
    """
    commands for users change
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, money):
        """

        :param ctx: context
        :type ctx: commands.Context
        :param member: member to give him some money
        :type member: discord.Member
        :param money: money to give
        :type money: int
        """
        if money.isdigit() or (money[1:].isdigit() and money[0] == "-"):
            money = int(money)
        else:
            await ctx.send("Введите число.")
            return
        with con.cursor() as cur:
            prev_money = cor.fetch_val("SELECT money FROM user WHERE user_id = %s AND guil_id = %s;", member.id, ctx.guild.id)
            if -2147483648 <= prev_money + money <= 2147483649:
                cur.execute("UPDATE users SET money = %s WHERE user_id = %s AND guild_id = %s;", prev_money + money,
                        member.id,
                        ctx.guild.id)
                await ctx.send("{} вам выдано {} монет".format(member.mention, money))
            else:
                await ctx.send("Образовались слишком большие числа :(")


def setup(bot):
    """
    setups bot

    :param bot: bot to setup
    :type bot: commands.Bot
    """
    bot.add_cog(BotChange(bot))
    bot.add_cog(UserChange(bot))
    print("Moderation finished")
