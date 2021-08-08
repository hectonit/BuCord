"""moderation cog"""
import discord
from discord.ext import commands

import utils
from utils.db import *


class BotChange(commands.Cog):
    """
    commands with changes of bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix="."):
        guild_info = await get_guild_info(ctx.guild.id)
        old_prefix = guild_info["prefix"]

        try:
            prefix.encode("ascii")
        except UnicodeEncodeError:
            emb = discord.Embed(color=0xf55c47)
            emb.title = "Ошибка"
            emb.add_field(name="Префикс не изменен!",
                          value="Префикс может содержать только ascii символы")
            emb.set_footer(text="Пример команды: {}help".format(old_prefix))
            await ctx.send(embed=emb)
            return

        if len(prefix) > 5:
            emb = discord.Embed(color=0xf55c47)
            emb.title = "Ошибка"
            emb.add_field(name="Префикс не изменен!",
                          value="Длина префикса не может превышать 5 символов")
            emb.set_footer(text="Пример команды: {}help".format(old_prefix))
            await ctx.send(embed=emb)
            return

        guild_info["prefix"] = prefix
        await update_guild(ctx.guild.id, guild_info)

        emb = discord.Embed(color=0x2ecc71)
        emb.title = "Обновление"
        emb.add_field(name="Новый префикс!", value="Префикс успешно изменен с {} на {}".format(
            old_prefix, prefix))
        emb.set_footer(text="Пример команды: {}help".format(prefix))
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def goodbye(self, ctx, *text):
        guild_info = await get_guild_info(ctx.guild.id)
        guild_info["goodbye"] = text
        await update_guild(ctx.guild.id, guild_info)
        await ctx.send("Прощание успешно изменено.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, *text):
        guild_info = await get_guild_info(ctx.guild.id)
        guild_info["welcome"] = text
        await update_guild(ctx.guild.id, guild_info)
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
        if money.isdigit() or (money[1:].isdigit() and money[0] == "-"):
            money = int(money)
        else:
            await ctx.send("Введите число.")
            return

        member_info = await get_member_info(member.id, ctx.guild.id)
        prev_money = member_info["money"]
        if -2147483648 <= prev_money + money <= 2147483649:
            member_info["money"] += money
            await update_member(member.id, ctx.guild.id, member_info)
            await ctx.send("{} вам выдано {} монет".format(member.mention, money))
        else:
            await ctx.send("Образовались слишком большие числа :(")


def setup(bot):
    bot.add_cog(BotChange(bot))
    bot.add_cog(UserChange(bot))
    print("Moderation finished")
