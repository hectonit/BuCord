import os
import platform
import random
import ssl
import sys

import asyncpg
import dbl
import discord
import requests
from discord.ext import commands, tasks

try:
    import configs
except ModuleNotFoundError:
    TOKEN = os.environ.get("DBL_TOKEN")
    DATABASE_URL = os.environ.get('DATABASE_URL')
    token = os.environ.get('BOT_TOKEN')
else:
    TOKEN = configs.dbltoken
    DATABASE_URL = configs.database
    token = configs.token


async def dynamic_prefix(pref_bot, message):
    guild = message.guild
    if guild is None:
        return await pref_bot.get_prefix(message)
    else:
        prefix = await pool.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1", guild.id)
        return prefix


bot = commands.Bot(command_prefix=dynamic_prefix)
bot.remove_command("help")
# for filename in os.listdir("./cogs"):
#    if filename.endswith(".py"):
#        bot.load_extension("cogs.{}".format(filename[:-3]))
dblpy = dbl.DBLClient(bot, TOKEN, autopost=True)

colors = [0x9b59b6, 0x1abc9c, 0x2ecc71, 0x3498db,
          0x34495e, 0x16a085, 0x27ae60, 0x2980b9, 0x8e44ad, 0x2c3e50,
          0xf1c40f, 0xe67e22, 0xe74c3c, 0xecf0f1,
          0x95a5a6, 0xf39c12, 0xd35400, 0xc0392b, 0xbdc3c7, 0x7f8c8d
          ]


def is_moder():
    def predicate(ctx):
        return True if ctx.author.permissions.administrator else False

    return commands.check(predicate)


def show_real_nick(member: discord.Member):
    return member.display_name + "#" + member.discriminator


@bot.event
async def on_ready():
    global pool
    ctx = ssl.create_default_context(cafile="")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    pool = await asyncpg.create_pool(DATABASE_URL, ssl=ctx)
    print("Database connected")
    ac_type = discord.ActivityType.listening
    name = ".help | {} servers".format(len(bot.guilds))
    activity = discord.Activity(name=name, type=ac_type)
    await bot.change_presence(activity=activity)
    for guild in bot.guilds:
        if len(guild.members) >= 10000 or guild.id == 264445053596991498:
            if guild.system_channel is not None:
                try:
                    await guild.system_channel.send(
                        "Ваш сервер слишком велик для нашего бота для того , чтобы он работал надо задонатить!!!")
                except discord.Forbidden:
                    pass
            continue
        guilds = await pool.fetchrow("SELECT * FROM guilds WHERE guild_id = $1;", guild.id)
        if guilds is None:
            await pool.execute(
                "INSERT INTO guilds (guild_id, welcome, goodbye, jackpot) VALUES ($1 , $2 , $3 , $4);",
                guild.id, "Здарова, {}", "Прощай, {}", 10000)
    for member in bot.get_all_members():
        if member.bot:
            continue
        users = await pool.fetchrow(
            "SELECT * FROM users WHERE user_id = $1 AND guild_id = $2;", member.id, member.guild.id)
        if users is None:
            await pool.execute(
                "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ($1,$2,$3,$4,$5,$6);",
                member.id, 0, 5, 0, 0, member.guild.id)

    worktime.start()
    mine.start()
    statuschange.start()
    print("Bot logged as {}".format(bot.user))


@bot.event
async def on_message(message):
    if message.guild is None or message.guild.id == 264445053596991498 or message.author.bot:
        return
    row = await pool.fetchrow(
        "SELECT level,points FROM users WHERE user_id = $1 AND guild_id = $2;",
        message.author.id, message.guild.id)
    points = row["points"]
    points += 1
    level = row["level"]
    if points >= 100:
        level += 1
        points -= 100
    await pool.execute(
        "UPDATE users SET money = money + 1 WHERE user_id = $1 AND guild_id = $2;", message.author.id,
        message.guild.id)
    await pool.execute(
        "UPDATE users SET points = $1 WHERE user_id = $2 AND guild_id = $3;", points, message.author.id,
        message.guild.id)
    await pool.execute(
        "UPDATE users SET level = $1 WHERE user_id = $2 AND guild_id = $3;", level, message.author.id,
        message.guild.id)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    prefix = await pool.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    if isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.send("Данная команда не найдена. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
    elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send(
            "Вы не задали необходимые аргументы. Прочитайте **{}help** , возможно вы ошиблись.".format(prefix))
    else:
        user_id = 530751275663491092
        user = bot.get_user(user_id)
        await user.send("Произошла ошибка:\n{}\nСервер:{}\nСообщение:{}".format(error, ctx.guild, ctx.message.content))
        await ctx.send("Произошла неожиданная ошибка, информация для дебага уже отправлена разработчикам.")


@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    text = await pool.fetchval(
        "SELECT welcome FROM guilds WHERE guild_id = $1;", guild.id)
    await pool.execute(
        "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ($1,$2,$3,$4,$5,$6);",
        member.id, 0, 5, 0, 0, guild.id)
    if channel is not None:
        await channel.send(text.format(member.mention))


@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    text = await pool.fetchval(
        "SELECT goodbye FROM guilds WHERE guild_id = $1;", guild.id)
    await pool.execute("DELETE FROM users WHERE user_id = $1 AND guild_id = $2;",
                       member.id, guild.id)
    if channel is not None:
        await channel.send(text.format(show_real_nick(member)))


@bot.event
async def on_guild_join(guild):
    user_id = 530751275663491092
    user = bot.get_user(user_id)
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
    await pool.execute("INSERT INTO guilds (guild_id) VALUES ($1);", guild.id)
    await channel.send(embed=emb)


@bot.event
async def on_guild_remove(guild):
    channel = guild.owner
    await channel.send("Эхххх....Жаль , что я вам не пригодился....\nP.S. Все данные удаляются")
    await pool.execute("DELETE FROM guilds WHERE guild_id = $1;", guild.id)


@bot.event
async def on_disconnect():
    await pool.execute("UPDATE botinfo SET worktime = 0;")
    print("DISCONNECTED")


@tasks.loop(minutes=5.0)
async def mine():
    for guild in bot.guilds:
        if guild.id == 264445053596991498:
            continue
        for member in guild.members:
            await pool.execute("UPDATE users SET minemoney = minemoney + 1 WHERE user_id = $1 AND guild_id = $2;",
                               member.id, guild.id)


@tasks.loop(hours=1.0)
async def statuschange():
    ac_type = discord.ActivityType.streaming
    name = ".help | {} servers".format(len(bot.guilds))
    activity = discord.Activity(name=name, type=ac_type)
    await bot.change_presence(activity=activity)


@tasks.loop(minutes=1.0)
async def worktime():
    await pool.execute("UPDATE botinfo SET worktime = worktime + 1;")


@bot.command()
async def stavka(ctx, arg):
    user_finance = await pool.fetchval(
        "SELECT money FROM users WHERE user_id = $1 AND guild_id = $2;", ctx.author.id, ctx.guild.id)
    arg = int(arg)
    if arg > user_finance or arg <= 0:
        await ctx.send("❌Число введено неверно.")
        return
    pot = random.randint(0, 100)
    if pot == 1:
        final_finance = arg * 10
        await ctx.send(
            "{}, поздравляем!Вы забрали джекпот!!!".format(ctx.author.mention))
    else:
        multi = random.randint(0, 20) / 10
        final_result = int(arg * multi)
        final_finance = user_finance - arg + final_result
        emb = discord.Embed(color=random.choice(colors))
        emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(
            arg, multi, final_result))
        await ctx.send(embed=emb)
    await pool.execute(
        "UPDATE users SET money = $1 WHERE user_id = $2 AND guild_id = $3;", final_finance,
        ctx.author.id,
        ctx.guild.id)


@bot.command()
async def balans(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    user_finance = await pool.fetchval(
        "SELECT money FROM users WHERE user_id = $1 AND guild_id = $2;",
        member.id, ctx.guild.id)
    emb.set_author(name="Баланс {} : {}$".format(
        show_real_nick(member), user_finance), icon_url=member.avatar_url)
    await ctx.send(embed=emb)


@bot.command()
async def usercard(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    row = await pool.fetchrow(
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


@bot.command()
async def top(ctx):
    emb = discord.Embed(color=random.choice(colors), title="Топ сервера {}".format(ctx.guild.name))
    title = "#{} - {}"
    value = "Монеты: **{}**"
    topp = await pool.fetch(
        "SELECT user_id,money FROM users WHERE guild_id = $1 ORDER BY money DESC;", ctx.guild.id)
    for ind, record in zip(range(1, 11), topp[:10]):
        member = bot.get_user(record["user_id"])
        subtitle = title.format(ind, show_real_nick(member))
        subvalue = value.format(record["money"])
        emb.add_field(name=subtitle, value=subvalue, inline=False)
    await ctx.send(embed=emb)


@bot.command()
@is_moder()
async def give(ctx, member: discord.Member, arg):
    arg = int(arg)
    await pool.execute("UPDATE users SET money = money+$1 WHERE user_id = $2 AND guild_id = $3;", arg,
                       member.id,
                       ctx.guild.id)
    await ctx.send("{} вам выдано {} монет".format(member.mention, arg))


@bot.command()
async def mine_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    mine_finance = await pool.fetchval(
        "SELECT minemoney FROM users WHERE user_id = $1 AND guild_id = $2;",
        member.id, ctx.guild.id)
    await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, mine_finance))


@bot.command()
async def miningvivod(ctx, arg):
    arg = int(arg)
    mine_finance = await pool.fetchval(
        "SELECT minemoney,money FROM users WHERE user_id = $1 AND guild_id = $2;",
        ctx.author.id, ctx.guild.id)
    if arg > mine_finance:
        await ctx.send("Число введено неверно.")
    else:
        await pool.execute(
            "UPDATE users SET minemoney = minemoney - $1 WHERE user_id = $2 AND guild_id = $3;", arg,
            ctx.author.id,
            ctx.guild.id)
        await pool.execute(
            "UPDATE users SET money = money + $1 WHERE user_id = $2 AND guild_id = $3;", arg, ctx.author.id,
            ctx.guild.id)
        await ctx.send("Вы успешно вывели {} монет".format(arg))


@bot.command()
async def dollar(ctx):
    r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    course = r.json()
    course = course["Valute"]["USD"]["Value"]
    await ctx.send("Курс доллара: {} рублей".format(course))


commands_descriptions = {
    "help": {
        "info": "выводит справку по командам",
        "use": "{}help [команда или секция]",
    },
    "dollar": {
        "info": "выводит курс доллара к рублю",
        "use": "{}dollar",
    },
    "balans": {
        "info": "выводит баланс участника",
        "use": "{}balans [участник сервера]",
    },
    "give": {
        "info": "добавляет участнику указанное кол-во монет(только для модераторов)",
        "use": "{}give <учатсник сервера> <монеты>",
    },
    "mine_info": {
        "info": "выводит кол-во намайненых монет участника",
        "use": "{}mine_info [участник сервера]",
    },
    "miningvivod": {
        "info": "выводит монеты с майнинга на баланс",
        "use": "{}miningvivod <монеты>",
    },
    "stavka": {
        "info": "вы ставите монеты(принцип как в казино)",
        "use": "{}stavka <монеты>",
    },
    "top": {
        "info": "выводит топ участников по монетам",
        "use": "{}top",
    },
    "usercard": {
        "info": "выводит карточку участника",
        "use": "{}usercard [участник сервера]",
    },
    "goodbye": {
        "info": "настраивает прощание",
        "use": "{}goodbye <текст , символами {} обозначьте участника>",
    },
    "welcome": {
        "info": "настраивает приветствие",
        "use": "{}welcome <текст , символами {} обозначьте участника>",
    },
    "findbug": {
        "info": "отправляет разработчикам информацию о баге",
        "use": "{}findbug \"<краткое описание бага>\" \"<полное описание бага>\" [url-адрес картинки]",
    },
    "botinfo": {
        "info": "выводит информацию о боте",
        "use": "{}botinfo",
    },
    "ping": {
        "info": "выводит пинг бота",
        "use": "{}ping",
    },
    "change_prefix": {
        "info": "изменяет префикс бота",
        "use": "{}change_prefix [префикс]",
    }
}


@bot.command(name="help")
async def help_(ctx, command_name=None):
    prefix = await pool.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1;", ctx.guild.id)
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
        emb.description = "`balans`,`mine_info`,`miningvivod`,`stavka`,`top`"
        emb.set_footer(text=base_command)
    elif command_name == "общее":
        emb.title = "Общие команды"
        emb.description = "`dollar`,`usercard`,`findbug`,`botinfo`,`ping`"
        emb.set_footer(text=base_command)
    else:
        emb.title = "Команда {}".format(command_name)
        command = commands_descriptions[command_name]
        emb.description = command["info"]
        emb.add_field(name="Использование:", value=command["use"].format(prefix))
        emb.set_footer(text="<аргумент> - обязательный аргумент , [аргумент] - необязательный аргумент")
    await ctx.send(embed=emb)


@bot.command()
@is_moder()
async def welcome(ctx, text):
    await pool.execute(
        "UPDATE guilds SET welcome = $1 WHERE guild_id = $2;", text, ctx.guild.id)
    await ctx.send("Приветствие успешно изменено.")


@bot.command()
@is_moder()
async def goodbye(ctx, text):
    await pool.execute(
        "UPDATE guilds SET goodbye = $1 WHERE guild_id = $2;", text, ctx.guild.id)
    await ctx.send("Прощание успешно изменено.")


@bot.command()
async def findbug(ctx, title, description, image_url=None):
    user_id = 530751275663491092
    user = bot.get_user(user_id)
    emb = discord.Embed(title=title, description=description)
    if image_url is not None:
        emb.set_image(url=image_url)
    emb.set_author(name=ctx.author)
    await user.send(embed=emb)
    await ctx.send("Спасибо за то , что вы помогаете нам улучшить бота.")


@bot.command()
async def botinfo(ctx):
    emb = discord.Embed(color=random.choice(colors))
    emb.add_field(name="ОС:", value="```{}```".format(sys.platform))
    emb.add_field(name="Сервера:", value="```{}```".format(len(bot.guilds)))
    emb.add_field(name="CPU:", value="```{}```".format(platform.processor()))
    work = await pool.fetchval("SELECT worktime FROM botinfo;")
    hours = work // 60
    minutes = work % 60
    emb.add_field(name="Время работы:", value=("```{} часов , {} минут```".format(hours, minutes)))
    await ctx.send(embed=emb)


@bot.command()
async def ping(ctx):
    emb = discord.Embed(color=random.choice(colors))
    emb.title = "Понг!"
    emb.description = "Пинг бота составляет {} ms".format(int(bot.latency * 1000))
    await ctx.send(embed=emb)


@bot.command()
@is_moder()
async def change_prefix(ctx, prefix="."):
    old_prefix = await pool.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1;", ctx.guild.id)
    await pool.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2;", prefix, ctx.guild.id)
    emb = discord.Embed(color=0x2ecc71)
    emb.title = "Обновление!!!"
    emb.add_field(name="Новый префикс!", value="Префикс успешно изменен с {} на {}".format(old_prefix, prefix))
    emb.set_footer(text="Пример команды: {}help".format(prefix))
    await ctx.send(embed=emb)


@bot.command(name="ban")
@is_moder()
async def ban_(ctx, member: discord.Member, del_message: int = 1, *, reason=None):
    await member.ban(reason=reason, delete_message_days=del_message)
    emb = discord.Embed(color=random.choice(colors))
    emb.title = ""
    emb.description = ""
    await ctx.send(embed=emb)


@bot.command(name="unban")
@is_moder()
async def unban_(ctx, member: discord.Member, *, reason=None):
    await member.unban(reason=reason)
    emb = discord.Embed(color=random.choice(colors))
    emb.title = ""
    emb.description = ""
    await ctx.send(embed=emb)


@bot.command(name="kick")
@is_moder()
async def kick_(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    emb = discord.Embed(color=random.choice(colors))
    emb.title = ""
    emb.description = ""
    await ctx.send(embed=emb)


bot.run(str(token))
