"""general cog"""
import platform
import random
import sys

import discord
import requests
from discord.ext import commands, tasks

from constraints import colors, commands_descriptions
from useful_commands import show_real_nick, create_loop

con = create_loop()


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
        ac_type = discord.ActivityType.listening
        name = ".help | {} servers".format(len(self.bot.guilds))
        activity = discord.Activity(name=name, type=ac_type)
        await self.bot.change_presence(activity=activity)
        # guild check
        for guild in self.bot.guilds:
            if len(guild.members) >= 10000 or guild.id == 264445053596991498:
                if guild.system_channel is not None:
                    try:
                        await guild.system_channel.send(
                            "Ваш сервер слишком велик для нашего бота для того , чтобы он работал надо задонатить!!!")
                    except discord.Forbidden:
                        pass
                continue
            guilds = await con.fetchrow("SELECT * FROM guilds WHERE guild_id = $1;", guild.id)
            if guilds is None:
                await con.execute("INSERT INTO guilds (guild_id) VALUES ($1);", guild.id)
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
        if message.guild is None or message.guild.id == 264445053596991498 or message.author.bot:
            return
        row = await con.fetchrow(
            "SELECT level,points FROM users WHERE user_id = $1 AND guild_id = $2;",
            message.author.id, message.guild.id)
        points = row["points"]
        points += 1
        level = row["level"]
        if points >= 100:
            level += 1
            points -= 100
        await con.execute(
            "UPDATE users SET points = $1 WHERE user_id = $2 AND guild_id = $3;", points, message.author.id,
            message.guild.id)
        await con.execute(
            "UPDATE users SET level = $1 WHERE user_id = $2 AND guild_id = $3;", level, message.author.id,
            message.guild.id)
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_disconnect(self):
        """
        do when bot disconnect
        """
        await con.execute("UPDATE bot_info SET work_time = 0;")
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
        await con.execute("UPDATE bot_info SET work_time = work_time + 1;")

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
        row = await con.fetchrow(
            "SELECT level,points FROM users WHERE user_id = $1 AND guild_id = $2;",
            ctx.author.id, ctx.guild.id)
        level = row["level"]
        points = row["points"]
        emb = discord.Embed(color=random.choice(colors))
        emb.set_thumbnail(url=member.avatar_url)
        emb.title = "Профиль участника {}".format(show_real_nick(member))
        emb.add_field(name="Уровень", value=level)
        emb.add_field(name="Очки", value=points)
        await ctx.send(embed=emb)

    @commands.command()
    async def dollar(self, ctx):
        """
        shows course of dollar

        :param ctx: context
        :type ctx: commands.Context
        """
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        course = r.json()
        course = course["Valute"]["USD"]["Value"]
        await ctx.send("Курс доллара: {} рублей".format(course))

    @commands.command(name="bot_info")
    async def info_bot_com(self, ctx):
        """
        shows info of bot

        :param ctx: context
        :type ctx: commands.Context
        """
        emb = discord.Embed(color=random.choice(colors))
        emb.add_field(name="ОС:", value="```{}```".format(sys.platform))
        emb.add_field(name="Сервера:", value="```{}```".format(len(self.bot.guilds)))
        emb.add_field(name="CPU:", value="```{}```".format(platform.processor()))
        work = await con.fetchval("SELECT work_time FROM bot_info;")
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
        emb = discord.Embed(color=random.choice(colors))
        emb.title = "Понг!"
        emb.description = "Пинг бота составляет {} ms".format(int(self.bot.latency * 1000))
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
        user_id = 530751275663491092
        user = self.bot.get_user(user_id)
        emb = discord.Embed(color=random.choice(colors))
        emb.title = "У нас новый сервер !!!"
        emb.description = "Название сервера: {}".format(guild.name)
        emb.set_image(url=guild.icon)
        await user.send(embed=emb)
        channel = guild.system_channel
        please = "Пожалуйста настройте бота!!!\n"
        advice = "Введите .help и просмотрите комнады в секции 'модерация'\n"
        some = "Надеюсь бот вам понравится!\n"
        support = "SUPPORT email: progcuber@gmail.com"
        emb = discord.Embed(color=random.choice(colors),
                            description=please + advice + some + support)
        await con.execute("INSERT INTO guilds (guild_id) VALUES ($1);", guild.id)
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
        await con.execute("DELETE FROM guilds WHERE guild_id = $1;", guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        do when member join

        :param member: member who join
        :type member: discord.Member
        :return: None
        :rtype: None
        """
        guild = member.guild
        channel = guild.system_channel
        if guild.id == 264445053596991498:
            return
        text = await con.fetchval(
            "SELECT welcome FROM guilds WHERE guild_id = $1;", guild.id)
        await con.execute(
            "INSERT INTO users (user_id,guild_id) VALUES ($1,$2);",
            member.id, guild.id)
        if channel is not None:
            await channel.send(text.format(member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        say goodbye to member

        :param member: member who leave
        :type member: discord.Member
        :return: None
        :rtype: None
        """
        guild = member.guild
        channel = guild.system_channel
        if guild.id == 264445053596991498:
            return
        text = await con.fetchval(
            "SELECT goodbye FROM guilds WHERE guild_id = $1;", guild.id)
        await con.execute("DELETE FROM users WHERE user_id = $1 AND guild_id = $2;",
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
        prefix = await con.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send("Данная команда не найдена. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send(
                "Вы не задали необходимые аргументы. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
        else:
            user_id = 530751275663491092
            user = self.bot.get_user(user_id)
            await user.send(
                "Произошла ошибка:\n{}\nСервер:{}\nСообщение:{}".format(error, ctx.guild, ctx.message.content))
            await ctx.send("Произошла неожиданная ошибка, информация для дебага уже отправлена разработчикам.")

    @commands.command(name="help")
    async def help_(self, ctx, command_name=None):
        """
        help command

        :param ctx: context
        :type ctx: commands.Context
        :param command_name: name to output only one type of commands
        :type command_name: str
        """
        prefix = await con.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        base_command = "Чтобы увидеть информацию об определенной команде пишите {}help `команда`".format(prefix)
        base_section = "Чтобы увидеть информацию об определенной секции пишите {}help `секция`".format(prefix)
        emb = discord.Embed(color=random.choice(colors))
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
            emb.description = "`balance`,`mine_info`,`withdrawal`,`bet`,`top`"
            emb.set_footer(text=base_command)
        elif command_name == "общее":
            emb.title = "Общие команды"
            emb.description = "`dollar`,`user_card`,`find_bug`,`bot_info`,`ping`, `help`"
            emb.set_footer(text=base_command)
        else:
            emb.title = "Команда {}".format(command_name)
            command = commands_descriptions[command_name]
            emb.description = command["info"]
            emb.add_field(name="Использование:", value=command["use"].format(prefix))
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
        user_id = 530751275663491092
        user = self.bot.get_user(user_id)
        emb = discord.Embed(title=title, description=description)
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
