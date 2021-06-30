"""economy cog"""
import random

import discord
from discord.ext import commands

from useful_commands import show_real_nick, connect

con = connect()


class General(commands.Cog):
    """
    general economy class
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        """
        output member balance

        :param ctx: context
        :type ctx: commands.Context
        :param member: member
        :type member: discord.Member
        """
        if member is None:
            member = ctx.author
        emb = discord.Embed(color=discord.Colour.random())
        with con.cursor() as cur:
            user_finance = cur.fetch_val("SELECT money FROM users WHERE user_id = %s AND guild_id = %s;",
                                         member.id, ctx.guild.id)
        emb.set_author(name="Баланс {} : {}$".format(
            show_real_nick(member), user_finance), icon_url=member.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def top(self, ctx):
        """
        output top of server by money

        :param ctx: context
        :type ctx: commands.Context
        """
        emb = discord.Embed(color=discord.Colour.random(), title="Топ сервера {}".format(ctx.guild.name))
        title = "#{} - {}"
        value = "Монеты: **{}**"
        with con.cursor() as cur:
            top_users = cur.fetch(
                "SELECT user_id,money FROM users WHERE guild_id = %s ORDER BY money DESC;", ctx.guild.id)
        for ind, record in zip(range(1, 11), top_users[:10]):
            member = self.bot.get_user(record["user_id"])
            subtitle = title.format(ind, show_real_nick(member))
            sub_value = value.format(record["money"])
            emb.add_field(name=subtitle, value=sub_value, inline=False)
        await ctx.send(embed=emb)


class Casino(commands.Cog):
    """
    class for casino functions
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bet(self, ctx, money):
        """
        bet some money

        :param ctx: context
        :type ctx: commands.Context
        :param money: amount of money to bet
        :type money: int
        :return: None
        :rtype: None
        """
        with con.cursor() as cur:
            user_finance = cur.fetch_val("SELECT money FROM users WHERE user_id = %s AND guild_id = %s;",
                                         ctx.author.id, ctx.guild.id)
            if money == "all":
                money = user_finance
            elif money.isdigit():
                money = int(money)
            else:
                await ctx.send("Введите число.")
                return
            if money > user_finance or money <= 0:
                await ctx.send("Число введено неверно.")
                return
            pot = random.randint(0, 100)
            if pot == 1:
                final_finance = money * 10
                await ctx.send(
                    "{}, поздравляем!Вы забрали джекпот!!!".format(ctx.author.mention))
            else:
                multi = random.randint(0, 20) / 10
                final_result = int(money * multi)
                final_finance = user_finance - money + final_result
                emb = discord.Embed(color=discord.Colour.random())
                emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(
                    money, multi, final_result))
                await ctx.send(embed=emb)
            if -2147483648 <= final_finance <= 2147483649:
                cur.execute(
                    "UPDATE users SET money = %s WHERE user_id = %s AND guild_id = %s;", final_finance,
                                                                                         ctx.author.id,
                                                                                         ctx.guild.id)
            else:
                await ctx.send("Образовались слишком большие числа :(")


def setup(bot):
    """
    setup cog

    :param bot: discord bot
    :type bot: commands.Bot
    """
    bot.add_cog(General(bot))
    bot.add_cog(Casino(bot))
    print("Economy finished")
