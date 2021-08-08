"""general cog"""
import platform
import sys
import time

import aiohttp
import discord
from discord.ext import commands, tasks

import configs
import utils
from configs.constants import commands_descriptions, MAX_MEMBERS, MY_ID
from utils.utils import show_real_nick, redis_connect
from utils.db import *


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        members = await get_all_members()
        for record in members:
            is_member = self.bot.get_user(record["user_id"])
            if is_member is None:
                await delete_member(record["user_id"], record["guild_id"])

        self.change_presence.start()
        redis_con.set("work_time", int(time.time()))
        print("Bot logged as {}".format(self.bot.user))

    @commands.Cog.listener()
    async def on_message(self, message):
        member = message.author

        if member.bot:
            return

        guild = message.guild
        is_guild = await get_guild_info(guild.id)
        if is_guild is None and guild.member_count < MAX_MEMBERS and guild.name:
            await create_guild(guild.id)
            for member in guild.members:
                await create_member(member.id, guild.id)

        member_info = await get_member_info(member.id, guild.id)
        if member_info is None:
            await create_member(member.id, guild.id)

        member_info = await get_member_info(member.id, guild.id)
        member_info["points"] += 1
        member_info["money"] += 1
        await update_member(member.id, guild.id, member_info)

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("DISCONNECTED")

    @tasks.loop(hours=3.0)
    async def change_presence(self):
        activity_type = discord.ActivityType.streaming
        name = ".help | {} servers".format(len(self.bot.guilds))
        activity = discord.Activity(name=name, type=activity_type)
        await self.bot.change_presence(activity=activity)

    @commands.command()
    async def user_card(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        member_info = await get_member_info(member.id, ctx.guild.id)
        level = member_info["points"] // 100
        points = member_info["points"] % 100

        emb = discord.Embed(color=discord.Colour.random())
        emb.set_thumbnail(url=member.avatar_url)
        emb.title = "Профиль участника {}".format(show_real_nick(member))
        emb.add_field(name="Уровень", value=level)
        emb.add_field(name="Очки", value=points)

        await ctx.send(embed=emb)

    @commands.command()
    async def exchange_rate(self, ctx, valute_to="RUB", valute_from="RUB"):
        """
        shows exchange rate of different valutes
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.cbr-xml-daily.ru/daily_json.js") as response:
                result = await response.json(content_type="application/javascript")

                if (not result["Valute"].get(valute_to) and valute_to != "RUB") or (not result["Valute"].get(valute_from) and valute_from != "RUB"):
                    await ctx.send("Неверный код валюты")
                    return

                valute_to_in_rub = 1
                if valute_to != "RUB":
                    valute_to_in_rub = result["Valute"][valute_to]["Value"] / \
                        result["Valute"][valute_to]["Nominal"]
                valute_from_in_rub = 1
                if valute_from != "RUB":
                    valute_from_in_rub = result["Valute"][valute_from]["Value"] / \
                        result["Valute"][valute_from]["Nominal"]

        await ctx.send("Exchange rate of {} : {} {}".format(valute_from, valute_from_in_rub / valute_to_in_rub, valute_to))

    @commands.command(name="bot_info")
    async def command_bot_info(self, ctx):
        work_time = int(time.time()) - int(redis_con.get("work_time"))
        work_time_min = work_time // 60
        hours = work_time_min // 60
        minutes = work_time_min % 60

        emb = discord.Embed(color=discord.Colour.random())
        emb.add_field(name="ОС:", value="```{}```".format(sys.platform))
        emb.add_field(name="Сервера:", value="```{}```".format(
            len(self.bot.guilds)))
        emb.add_field(name="CPU:", value="```{}```".format(
            platform.processor()))
        emb.add_field(name="Время работы:",
                      value="```{} mins, {} hours```".format(minutes, hours))
        await ctx.send(embed=emb)

    @commands.command()
    async def ping(self, ctx):
        emb = discord.Embed(color=discord.Colour.random())
        emb.title = "Понг!"
        emb.description = "Пинг бота составляет {} ms".format(
            self.bot.latency * 1000)
        await ctx.send(embed=emb)


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        await create_guild(guild.id)
        for member in guild.members:
            await create_member(member.id)

        channel = guild.system_channel
        emb = discord.Embed(color=discord.Colour.random(),
                            description="Hello!\nType `.help`.")
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await delete_guild(guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        guild = member.guild
        channel = guild.system_channel
        guild_info = await get_guild_info(guild.id)
        text = guild_info["welcome"]
        await create_member(member.id)
        if channel is not None:
            await channel.send(text)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        guild = member.guild
        channel = guild.system_channel
        guild_info = await get_guild_info(guild.id)
        text = guild_info["welcome"]
        delete_member(member.id)
        if channel is not None:
            await channel.send(text)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        guild_info = await get_guild_info(ctx.guild.id)
        prefix = guild_info["prefix"]
        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send("Данная команда не найдена. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send(
                "Вы не задали необходимые аргументы. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        else:
            await ctx.send("Произошла неожиданная ошибка")
            raise error

    @commands.command(name="help")
    async def help_(self, ctx, command_name=None):
        guild_info = await get_guild_info(ctx.guild.id)
        prefix = guild_info["prefix"]

        base_command = "Чтобы увидеть информацию об определенной команде пишите {}help `команда`".format(
            prefix)
        base_section = "Чтобы увидеть информацию об определенной секции пишите {}help `секция`".format(
            prefix)

        emb = discord.Embed(color=discord.Colour.random())

        if command_name is None:
            emb.title = "Секции команд бота BuCord:"
            emb.description = "`модерация`,`экономика`,`общее`, `игры`"
            emb.set_footer(text=base_section)
        elif command_name == "модерация":
            emb.title = "Команды для модерации"
            emb.description = "`give`,`goodbye`,`welcome`,`change_prefix`"
            emb.set_footer(text=base_command)
        elif command_name == "экономика":
            emb.title = "Команды для экономики"
            emb.description = "`balance`,`bet`,`top`"
            emb.set_footer(text=base_command)
        elif command_name == "общее":
            emb.title = "Общие команды"
            emb.description = "`exchange_rate`,`user_card`,`find_bug`,`bot_info`,`ping`, `help`"
            emb.set_footer(text=base_command)
        elif command_name == "игры":
            emb.title = "Команды для игр"
            emb.description = "`tictactoe`"
            emb.set_footer(text=base_command)
        else:
            emb.title = "Команда {}".format(command_name)

            try:
                command = commands_descriptions[command_name]
            except KeyError:
                await ctx.send("Команда не найдена")
                return

            emb.description = command["info"]
            emb.add_field(name="Использование:", value=prefix + command["use"])
            emb.set_footer(
                text="<аргумент> - обязательный аргумент , [аргумент] - необязательный аргумент")

        await ctx.send(embed=emb)

    @commands.command()
    async def find_bug(self, ctx, title, description, image_url=None):
        user = self.bot.get_user(MY_ID)

        emb = discord.Embed(title=title, description=description,
                            color=discord.Colour.random())
        if image_url is not None:
            emb.set_image(url=image_url)

        emb.set_author(name=ctx.author)
        await user.send(embed=emb)
        await ctx.send("Спасибо за то, что вы помогаете нам улучшить бота.")


def setup(bot):
    bot.add_cog(Statistics(bot))
    bot.add_cog(Other(bot))
    print("General finished")
