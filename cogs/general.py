"""general cog"""
import platform
import sys

import aiohttp
import discord
from discord.ext import commands, tasks

from constraints import commands_descriptions, MAX_MEMBERS, MY_ID
from useful_commands import show_real_nick, connect

con = connect()


class Stuff(commands.Cog):
    """
    commands for showing stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready event
        """
        ac_type = discord.ActivityType.streaming
        name = ".help | {} servers".format(len(self.bot.guilds))
        activity = discord.Activity(name=name, type=ac_type)
        await self.bot.change_presence(activity=activity)

        for guild in self.bot.guilds:
            if guild.name and guild.member_count < MAX_MEMBERS:
                with con.cursor() as cur:
                    guilds = cur.fetch_row("SELECT * FROM guilds WHERE guild_id = %s;", guild.id)
                    if guilds is None:
                        cur.execute("INSERT INTO guilds (guild_id) VALUES (%s);", guild.id)
                        for member in guild.members:
                            if not member.bot:
                                cur.execute("INSERT INTO users (user_id,guild_id) VALUES (%s,%s);",
                                            member.id, guild.id)
        with con.cursor() as cur:
            members = cur.fetch("SELECT * FROM users;")
            for row in members:
                is_member = self.bot.get_user(row["user_id"])
                if is_member is None:
                    cur.execute("DELETE FROM users WHERE user_id = %s AND guild_id = %s;", row["user_id"],
                                row["guild_id"])
        self.status_change.start()
        self.work_time.start()
        print("Bot logged as {}".format(self.bot.user))

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        event that check every message

        :param message: each message
        :type message: discord.Message
        :return: None
        :rtype: None
        """
        if message.author.bot:
            return
        with con.cursor() as cur:
            row = cur.fetch_row("SELECT level,points FROM users WHERE user_id = %s AND guild_id = %s;",
                                message.author.id, message.guild.id)
            points = row["points"]
            points += 1
            level = row["level"]
            if points == 100:
                level += 1
                points = 0
            cur.execute(
                "UPDATE users SET points = %s WHERE user_id = %s AND guild_id = %s;", points, message.author.id,
                message.guild.id)
            cur.execute(
                "UPDATE users SET level = %s WHERE user_id = %s AND guild_id = %s;", level, message.author.id,
                message.guild.id)
            cur.execute(
                "UPDATE users SET money = money + 1 WHERE user_id = %s AND guild_id = %s;", message.author.id,
                message.guild.id)

    @commands.Cog.listener()
    async def on_disconnect(self):
        """
        do when bot disconnect
        """
        with con.cursor() as cur:
            cur.execute("UPDATE bot_info SET work_time = 0;")
        print("DISCONNECTED")

    @tasks.loop(hours=1.0)
    async def status_change(self):
        """
        change status of bot
        """
        ac_type = discord.ActivityType.streaming
        name = ".help | {} servers".format(len(self.bot.guilds))
        activity = discord.Activity(name=name, type=ac_type)
        await self.bot.change_presence(activity=activity)

    @tasks.loop(minutes=1.0)
    async def work_time(self):
        """
        plus work_time for stuff
        """
        with con.cursor() as cur:
            cur.execute("UPDATE bot_info SET work_time = work_time + 1;")

    @commands.command()
    async def user_card(self, ctx, member: discord.Member = None):
        """
        shows user_card of member

        :param ctx: context
        :type ctx: commands.Context
        :param member: member to know user_card
        :type member: discord.Member
        """
        if member is None:
            member = ctx.author
        with con.cursor() as cur:
            row = cur.fetch_row("SELECT level,points FROM users WHERE user_id = %s AND guild_id = %s;",
                                ctx.author.id, ctx.guild.id)
        level = row["level"]
        points = row["points"]
        emb = discord.Embed(color=discord.Colour.random())
        emb.set_thumbnail(url=member.avatar_url)
        emb.title = "Профиль участника {}".format(show_real_nick(member))
        emb.add_field(name="Уровень", value=level)
        emb.add_field(name="Очки", value=points)
        await ctx.send(embed=emb)

    @commands.command()
    async def course(self, ctx, valute="USD"):
        """
        shows course of dollar

        :param valute: abbreviation of valute
        :type valute: str
        :param ctx: context
        :type ctx: commands.Context
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.cbr-xml-daily.ru/daily_json.js") as response:
                json = await response.json(content_type="application/javascript")
                try:
                    course = json["Valute"][valute]["Value"] / json["Valute"][valute]["Nominal"]
                except KeyError:
                    await ctx.send("Неверный код валюты")
                    return
        await ctx.send("Курс {}: {} рублей".format(json["Valute"][valute]["Name"], course))

    @commands.command(name="bot_info")
    async def info_bot_com(self, ctx):
        """
        shows info of bot

        :param ctx: context
        :type ctx: commands.Context
        """
        emb = discord.Embed(color=discord.Colour.random())
        emb.add_field(name="ОС:", value="```{}```".format(sys.platform))
        emb.add_field(name="Сервера:", value="```{}```".format(len(self.bot.guilds)))
        emb.add_field(name="CPU:", value="```{}```".format(platform.processor()))
        with con.cursor() as cur:
            work = cur.fetch_val("SELECT work_time FROM bot_info;")
        hours = work // 60
        minutes = work % 60
        emb.add_field(name="Время работы:", value=("```{} часов , {} минут```".format(hours, minutes)))
        await ctx.send(embed=emb)

    @commands.command()
    async def ping(self, ctx):
        """
        shows ping of bot

        :param ctx: context
        :type ctx: commands.Context
        """
        emb = discord.Embed(color=discord.Colour.random())
        emb.title = "Понг!"
        emb.description = "Пинг бота составляет {} ms".format(self.bot.latency * 1000)
        await ctx.send(embed=emb)


class Other(commands.Cog):
    """
    other commands those cant be in other groups
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        do when bot join to new guild

        :param guild: guild what bot join
        :type guild: discord.Guild
        """
        with con.cursor() as cur:
            cur.execute("INSERT INTO guilds (guild_id) VALUES (%s);", (guild.id,))
            for member in guild.members:
                cur.execute("INSERT INTO users (user_id,guild_id) VALUES (%s,%s);", (member.id, guild.id))
        channel = guild.system_channel
        please = "Пожалуйста настройте бота!!!\n"
        advice = "Введите .help и просмотрите комнады в секции 'модерация'\n"
        hope = "Надеюсь бот вам понравится!\n"
        support = "SUPPORT email: progcuber@gmail.com"
        emb = discord.Embed(color=discord.Colour.random(),
                            description=please + advice + hope + support)
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        do when bot leave some guild

        :param guild: guild what bot leave
        :type guild: discord.Guild
        """
        channel = guild.owner
        await channel.send("Эхххх....Жаль , что я вам не пригодился....\nP.S. Все данные удаляются")
        with con.cursor() as cur:
            cur.execute("DELETE FROM guilds WHERE guild_id = $1;", (guild.id,))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        do when member join

        :param member: member who join
        :type member: discord.Member
        """
        if member.bot:
            return
        guild = member.guild
        channel = guild.system_channel
        with con.cursor() as cur:
            text = cur.fetch_val("SELECT welcome FROM guilds WHERE guild_id = %s;", guild.id)
            cur.execute(
                "INSERT INTO users (user_id,guild_id) VALUES (%s,%s);",
                (member.id, guild.id))
        if channel is not None:
            await channel.send(text.format(member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        say goodbye to member

        :param member: member who leave
        :type member: discord.Member
        """
        if member.bot:
            return
        guild = member.guild
        channel = guild.system_channel
        with con.cursor() as cur:
            text = cur.fetch_val("SELECT goodbye FROM guilds WHERE guild_id = %s;", guild.id)
            cur.execute("DELETE FROM users WHERE user_id = %s AND guild_id = %s;",
                        member.id, guild.id)
        if channel is not None:
            await channel.send(text.format(show_real_nick(member)))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        send me a message with error

        :param ctx: context
        :type ctx: commands.Context
        :param error: error that occurred
        :type error: Exception
        """
        with con.cursor() as cur:
            prefix = cur.fetch_val("SELECT prefix FROM guilds WHERE guild_id = %s", ctx.guild.id)
        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send("Данная команда не найдена. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send(
                "Вы не задали необходимые аргументы. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        else:
            await ctx.send("Произошла неожиданная ошибка")

    @commands.command(name="help")
    async def help_(self, ctx, command_name=None):
        """
        help command

        :param ctx: context
        :type ctx: commands.Context
        :param command_name: name to output only one type of commands
        :type command_name: str
        """
        with con.cursor() as cur:
            prefix = cur.fetch_val("SELECT prefix FROM guilds WHERE guild_id = %s;", ctx.guild.id)
        base_command = "Чтобы увидеть информацию об определенной команде пишите {}help `команда`".format(prefix)
        base_section = "Чтобы увидеть информацию об определенной секции пишите {}help `секция`".format(prefix)
        emb = discord.Embed(color=discord.Colour.random())
        if command_name is None:
            emb.title = "Секции команд бота BuCord:"
            emb.description = "`модерация`,`экономика`,`общее`"
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
            emb.description = "`course`,`user_card`,`find_bug`,`bot_info`,`ping`, `help`"
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
            emb.set_footer(text="<аргумент> - обязательный аргумент , [аргумент] - необязательный аргумент")
        await ctx.send(embed=emb)

    @commands.command()
    async def find_bug(self, ctx, title, description, image_url=None):
        """
        send me a message with bug

        :param ctx: context
        :type ctx: commands.Context
        :param title: title of bug
        :type title: str
        :param description: detail description of bug
        :type description: str
        :param image_url: url of image of bug
        :type image_url: str
        """
        user = self.bot.get_user(MY_ID)
        emb = discord.Embed(title=title, description=description, color=discord.Colour.random())
        if image_url is not None:
            emb.set_image(url=image_url)
        emb.set_author(name=ctx.author)
        await user.send(embed=emb)
        await ctx.send("Спасибо за то , что вы помогаете нам улучшить бота.")


def setup(bot):
    """
    setup cog

    :param bot: discord bot
    :type bot: commands.Bot
    """
    bot.add_cog(Stuff(bot))
    bot.add_cog(Other(bot))
    print("General finished")
