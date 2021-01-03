"""economy cog"""
import random

import discord
from discord.ext import commands, tasks

from constraints import colors
from useful_commands import show_real_nick, create_loop

con = create_loop()


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
        emb = discord.Embed(color=random.choice(colors))
        user_finance = await con.fetchval(
            "SELECT money FROM users WHERE user_id = $1 AND guild_id = $2;",
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
        emb = discord.Embed(color=random.choice(colors), title="Топ сервера {}".format(ctx.guild.name))
        title = "#{} - {}"
        value = "Монеты: **{}**"
        top_users = await con.fetch(
            "SELECT user_id,money FROM users WHERE guild_id = $1 ORDER BY money DESC;", ctx.guild.id)
        for ind, record in zip(range(1, 11), top_users[:10]):
            member = self.bot.get_user(record["user_id"])
            subtitle = title.format(ind, show_real_nick(member) if member else "None")
            sub_value = value.format(record["money"])
            emb.add_field(name=subtitle, value=sub_value, inline=False)
        await ctx.send(embed=emb)


class Mining(commands.Cog):
    """
    class for mining and mining commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready event, check members
        """
        for member in self.bot.get_all_members():
            if member.bot:
                continue
            users = await con.fetchrow(
                "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2;", member.id, member.guild.id)
            if users is None:
                await con.execute(
                    "INSERT INTO users (user_id,guild_id) VALUES ($1,$2);",
                    member.id, member.guild.id)
        self.mine.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        update member balance on each message

        :param message: message from member
        :type message: discord.Message
        :return: None
        :rtype: None
        """
        if message.guild is None or message.guild.id == 264445053596991498 or message.author.bot:
            return
        await con.execute(
            "UPDATE users SET money = money + 1 WHERE user_id = $1 AND guild_id = $2;", message.author.id,
            message.guild.id)

    @tasks.loop(minutes=5.0)
    async def mine(self):
        """
        update mine_money of all members
        """
        for guild in self.bot.guilds:
            if guild.id == 264445053596991498:
                continue
            for member in guild.members:
                await con.execute("UPDATE users SET mine_money = mine_money + 1 WHERE user_id = $1 AND guild_id = $2;",
                                  member.id, guild.id)

    @commands.command()
    async def mine_info(self, ctx, member: discord.Member = None):
        """
        output mine_money of member

        :param ctx: context
        :type ctx: commands.Context
        :param member: member
        :type member: discord.Member
        """
        if member is None:
            member = ctx.author
        mine_finance = await con.fetchval(
            "SELECT mine_money FROM users WHERE user_id = $1 AND guild_id = $2;",
            member.id, ctx.guild.id)
        await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, mine_finance))

    @commands.command()
    async def withdrawal(self, ctx, mine_money):
        """
        withdrawal money from mine_money to money

        :param ctx: context
        :type ctx: commands.Context
        :param mine_money: mine_money
        :type mine_money: int
        """
        mine_money = int(mine_money)
        mine_finance = await con.fetchval(
            "SELECT mine_money FROM users WHERE user_id = $1 AND guild_id = $2;",
            ctx.author.id, ctx.guild.id)
        if mine_money > mine_finance:
            await ctx.send("Число введено неверно.")
        else:
            await con.execute(
                "UPDATE users SET mine_money = mine_money - $1 WHERE user_id = $2 AND guild_id = $3;", mine_money,
                ctx.author.id,
                ctx.guild.id)
            await con.execute(
                "UPDATE users SET money = money + $1 WHERE user_id = $2 AND guild_id = $3;", mine_money, ctx.author.id,
                ctx.guild.id)
            await ctx.send("Вы успешно вывели {} монет".format(mine_money))


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
        user_finance = await con.fetchval(
            "SELECT money FROM users WHERE user_id = $1 AND guild_id = $2;", ctx.author.id, ctx.guild.id)
        money = int(money)
        if money > user_finance or money <= 0:
            await ctx.send("❌Число введено неверно.")
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
            emb = discord.Embed(color=random.choice(colors))
            emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(
                money, multi, final_result))
            await ctx.send(embed=emb)
        await con.execute(
            "UPDATE users SET money = $1 WHERE user_id = $2 AND guild_id = $3;", final_finance,
            ctx.author.id,
            ctx.guild.id)


def setup(bot):
    """
    setup cog

    :param bot: discord bot
    :type bot: commands.Bot
    """
    bot.add_cog(Mining(bot))
    bot.add_cog(General(bot))
    bot.add_cog(Casino(bot))
    print("Economy finished")
