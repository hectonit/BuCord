"""economy cog"""
import random

import discord
from discord.ext import commands

import utils
from utils.utils import show_real_nick
from utils.db import *


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        member_info = await get_member_info(member.id, ctx.guild.id)
        user_balance = member_info["money"]

        emb = discord.Embed(color=discord.Colour.random())
        emb.set_author(name="Баланс {} : {}$".format(
            show_real_nick(member), user_balance), icon_url=member.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def top(self, ctx):
        emb = discord.Embed(color=discord.Colour.random(),
                            title="Топ сервера {}".format(ctx.guild.name))
        title = "#{} - {}"
        value = "Монеты: **{}**"

        top_users = await get_all_members_ordered(ctx.guild.id)
        for index, record in zip(range(1, 11), top_users[:10]):
            member = self.bot.get_user(record["user_id"])
            subtitle = title.format(index, show_real_nick(member))
            sub_value = value.format(record["money"])
            emb.add_field(name=subtitle, value=sub_value, inline=False)

        await ctx.send(embed=emb)


class Casino(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bet(self, ctx, money):
        member_info = await get_member_info(ctx.author.id, ctx.guild.id)
        user_balance = member_info["money"]

        if money == "all":
            money = user_balance
        elif money.isdigit():
            money = int(money)
        else:
            await ctx.send("Введите число.")
            return
        if money > user_balance or money <= 0:
            await ctx.send("Число введено неверно.")
            return

        rand = random.randint(0, 100)
        if rand == 1:
            final_balance = user_balance + money * 9
            await ctx.send(
                "{}, поздравляем!Вы забрали джекпот!!!".format(ctx.author.mention))
        else:
            multi = random.randint(0, 20) / 10
            final_result = int(money * multi)
            final_balance = user_balance - money + final_result

        if -2147483648 <= final_balance <= 2147483649:
            member_info["money"] = final_balance
            await update_member(ctx.author.id, ctx.guild.id, member_info)
            emb = discord.Embed(color=discord.Colour.random())
            emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(
                money, multi, final_result))
            await ctx.send(embed=emb)
        else:
            await ctx.send("Образовались слишком большие числа :(")


def setup(bot):
    bot.add_cog(General(bot))
    bot.add_cog(Casino(bot))
    print("Economy finished")
