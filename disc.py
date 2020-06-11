import discord
from discord.ext import commands
from discord import utils
import random
import os
import asyncio
import time
import requests
import json
import datetime
import psycopg2
from bs4 import BeautifulSoup as BS

bot = commands.Bot(command_prefix='.')
client = discord.Client()
bot.remove_command("help")

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode="require")

cursor = conn.cursor()

jackpot = 10000

dt = int(time.time())
dt = dt // 60

brawlplayers = {}

colors = [0xFF0000, 0x39d0d6, 0xff6699, 0x17f90f, 0x0f13f9, 0xdff90f, 0xff8100, 0x740001, 0x330066]


@bot.event
async def on_ready():
    global conn, cursor
    await bot.change_presence(activity=discord.Game(".help"))
    all_members = 0
    for guild in bot.guilds:
        all_members += len(guild.members)
        if all_members >= 10000 or guild.id == 264445053596991498:
            if len(guild.text_channels) <= 0:
                pass
            else:
                await guild.text_channels[0].send(
                    "Ваш сервер слишком велик для нашего бота для того , чтобы он работал надо задонатить!!!")
            continue
        if guild.system_channel == None:
            pass
        else:
            await guild.system_channel.send("Хей, я снова онлайн!")
        cursor.execute("SELECT * FROM guilds WHERE guild_id = %s", [str(guild.id)])
        guilds = cursor.fetchall()
        if len(guilds) == 0:
            cursor.execute(
                "INSERT INTO guilds (guild_id, moder_roles, welcome, goodbye, jackpot) VALUES (%s , %s , %s, %s , %s);",
                [str(guild.id), ["0"], "Здарова, {}", "Прощай, {}", 10000])
        for member in guild.members:
            if member.id == 706401122721595444:
                return
            cursor.execute(
                "SELECT * FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(member.id, guild.id))
            users = cursor.fetchall()
            if len(users) == 0:
                cursor.execute(
                    "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ('{}',{},{},{},{},'{}');".format(
                        member.id, 0, 5, 0, 0, guild.id))
            conn.commit()
    print("Bot logged as {}".format(bot.user))


@bot.event
async def on_message(message):
    global dt, cursor, conn
    if message.guild.id == 264445053596991498:
        return
    newdt = int(time.time())
    newdt = newdt // 60
    if message.author.id == 706401122721595444:
        return
    if newdt > dt:
        cursor.execute("SELECT * FROM users WHERE guild_id = '{}';".format(message.guild.id))
        otherides = cursor.fetchall()
        ides = []
        for elem in otherides:
            ides.append(elem[0])
        for id in ides:
            cursor.execute(
                "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
                    message.author.id, message.guild.id))
            minemoney = cursor.fetchall()
            minemoney = int(minemoney[0][3])
            minemoney = minemoney + newdt - dt
            cursor.execute(
                "UPDATE users SET minemoney = {} WHERE user_id = '{}' AND guild_id = '{}';".format(minemoney, id,
                                                                                                   message.guild.id))
            conn.commit()
        dt = newdt
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            message.author.id, message.guild.id))
    money = cursor.fetchall()
    money = int(money[0][2]) + 1
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            message.author.id, message.guild.id))
    points = cursor.fetchall()
    points = int(points[0][4]) + 1
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            message.author.id, message.guild.id))
    level = cursor.fetchall()
    level = level[0][1]
    if points >= 100:
        level += 1
        points -= 100
    cursor.execute(
        "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(money, message.author.id,
                                                                                       message.guild.id))
    cursor.execute(
        "UPDATE users SET points = {} WHERE user_id = '{}' AND guild_id = '{}';".format(points, message.author.id,
                                                                                        message.guild.id))
    cursor.execute(
        "UPDATE users SET level = {} WHERE user_id = '{}' AND guild_id = '{}';".format(level, message.author.id,
                                                                                       message.guild.id))
    cursor.execute(
        "UPDATE users SET guild_id = {} WHERE user_id = '{}' AND guild_id = '{}';".format(level, message.guild.id,
                                                                                          message.guild.id))
    conn.commit()
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send('Команда не найдена')


@bot.event
async def on_member_join(member):
    global conn, cursor
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    cursor.execute(
        "INSERT INTO users (user_id,level,money,minemoney,points,guild_id) VALUES ('{}',{},{},{},{},'{}');".format(
            member.id, 0, 5, 0, 0, guild.id))
    conn.commit()
    await channel.send("Здарова , {}".format(member.mention))


@bot.event
async def on_member_remove(member):
    global cursor, conn
    guild = member.guild
    channel = guild.system_channel
    if guild.id == 264445053596991498:
        return
    cursor.execute("DELETE FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(member.id, guild.id))
    conn.commit()
    await channel.send("Прощай , {}".format(member))


@bot.event
async def on_guild_join(guild):
    channel = guild.system_channel
    await channel.send("Пожалуйста настройте бота!!!")


# ready
@bot.command()
async def stavka(ctx, arg: int):
    global cursor, jackpot, colors, conn
    cursor.execute(
        "SELECT * FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(ctx.author.id, ctx.guild.id))
    userfinance = cursor.fetchall()
    arg = int(arg)
    if arg > userfinance[0][2] or arg <= 0:
        await ctx.send("❌Число введено неверно.")
    else:
        multi = random.randint(0, 20) / 10
        pot = random.randint(0, 100)
        finalresult = int(arg * multi)
        firstfinance = userfinance[0][2] - arg
        cursor.execute(
            "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(firstfinance, ctx.author.id,
                                                                                           ctx.guild.id))
        jackpot += arg
        jackpot -= finalresult
        emb = discord.Embed(color=random.choice(colors))
        emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(arg, multi, finalresult))
        if pot == 5:
            jackpotfinance = jackpot + userfinance[0][2]
            cursor.execute(
                "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(jackpotfinance,
                                                                                               ctx.author.id,
                                                                                               ctx.guild.id))
            await ctx.send(
                "{}, поздравляем!Вы забрали джекпот!!!Он составлял {} монет!!!".format(ctx.author.mention, jackpot))
            jackpot = 10000
        else:
            lastfinance = finalresult + firstfinance
            cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(lastfinance,
                                                                                                          ctx.author.id,
                                                                                                          ctx.guild.id))
            await ctx.send(embed=emb)
    conn.commit()


# ready
@bot.command()
async def balans(ctx, member: discord.Member = None):
    global colors, cursor
    if member == None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            member.id, ctx.guild.id))
    userfinance = cursor.fetchall()
    emb.set_author(name="Баланс {} : {}$".format(member, userfinance[0][2]), icon_url=member.avatar_url)
    await ctx.send(embed=emb)
    member = member


@bot.command()
async def usercard(ctx, member: discord.Member = None):
    global colors, cursor, conn
    if member == None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    usercardcomm = cursor.fetchall()
    emb.set_thumbnail(url=member.avatar_url)
    emb.title = "Профиль участника {}".format(member)
    emb.add_field(name="Уровень", value=("{}".format(usercardcomm[0][1])))
    emb.add_field(name="Очки", value=("{}".format(usercardcomm[0][4])))
    await ctx.send(embed=emb)
    member = member
    conn.commit()


@bot.command()
async def top(ctx):
    global cursor
    torr = []
    ind1 = "Нет информации"
    ind2 = "Нет информации"
    ind3 = "Нет информации"
    ind4 = "Нет информации"
    ind5 = "Нет информации"
    cursor.execute("SELECT * FROM users WHERE guild_id = '{}' ORDER BY money;".format(ctx.guild.id))
    topp = cursor.fetchall()
    topp.reverse()
    counter = 0
    for elem in topp:
        biggest = elem[2]
        bigkey = int(elem[0])
        torr.append([biggest, bigkey])
        if bot.get_user(torr[counter][1]) == None:
            torr.pop()
            continue
        counter += 1
    ind1 = ("Первое место - {} - {}".format(bot.get_user(torr[0][1]), torr[0][0]))
    if len(torr) >= 2:
        ind2 = ("Второе место - {} - {}".format(bot.get_user(torr[1][1]), torr[1][0]))
    if len(torr) >= 3:
        ind3 = ("Третье место - {} - {}".format(bot.get_user(torr[2][1]), torr[2][0]))
    if len(torr) >= 4:
        ind4 = ("Четвертое место - {} - {}".format(bot.get_user(torr[3][1]), torr[3][0]))
    if len(torr) >= 5:
        ind5 = ("Пятое место - {} - {}".format(bot.get_user(torr[4][1]), torr[4][0]))
    await ctx.send("{}\n{}\n{}\n{}\n{}".format(ind1, ind2, ind3, ind4, ind5))


@bot.command()
async def give(ctx, member: discord.Member, arg):
    global cursor, conn
    rolarr = []
    for role in ctx.author.roles:
        rolarr.append(role.id)
    moder = 706208121487360030
    if moder not in rolarr:
        await ctx.channel.send("У вас недостаточно прав")
        return
    arg = int(arg)
    cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(lastfinance,
                                                                                                  ctx.author.id,
                                                                                                  ctx.guild.id))
    await ctx.channel.send("{} вам выдано {} монет".format(member.mention, arg))
    member = member


@bot.command()
async def jackpot_info(ctx):
    await ctx.send("Джекпот составляет {} монет.".format(jackpot))


@bot.command()
async def mine_info(ctx, member: discord.Member = None):
    global dt
    if member == None:
        member = ctx.author
    newdt = int(time.time())
    newdt = newdt // 60
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            member.id, ctx.guild.id))
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3] + newdt - dt
    dt = newdt
    await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, minefinance))


@bot.command()
async def miningvivod(ctx, arg):
    global conn, cursor
    arg = int(arg)
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3]
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}' AND guild_id = '{}';".format(
            ctx.author.id, ctx.guild.id))
    finance = cursor.fetchall()
    finance = finance[0][2]
    if arg > minefinance:
        await ctx.send("Число введено неверно.")
    else:
        anoarg = arg
        arg = int(arg * 0.95)
        finance = finance + arg
        minefinance = minefinance - arg
        cursor.execute("UPDATE users SET minemoney = {} WHERE user_id = '{}' AND guild_id = '{}';".format(minefinance,
                                                                                                          ctx.author.id,
                                                                                                          ctx.guild.id))
        cursor.execute(
            "UPDATE users SET money = {} WHERE user_id = '{}' AND guild_id = '{}';".format(finance, ctx.author.id,
                                                                                           ctx.guild.id))
        await ctx.send("Вы успешно вывели {} монет".format(anoarg))
        conn.commit()


@bot.command()
async def dollar(ctx):
    r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    course = r.json()
    course = course['Valute']['USD']['Value']
    await ctx.send("Курс доллара: {} рублей".format(course))


@bot.command()
async def help(ctx, arg=None):
    global colors
    emb = discord.Embed(color=random.choice(colors))
    if arg == None:
        emb.title = "Команды бота BuCord*:"
        emb.description = "<> - обязательный аргумент , [] - необязательный аргумент"
        emb.add_field(name=".help [команда]", value="выводит это сообщение")
        emb.add_field(name=".dollar", value="выводит курс доллара к рублю")
        emb.add_field(name=".jackpot_info", value="выводит кол-во монет , которое составляет джекпот")
        emb.add_field(name=".balans [участник сервера]", value="выводит баланс участника")
        emb.add_field(name=".give <учатсник сервера> <монеты>",
                      value="добавляет участнику указанное кол-во монет(только для модераторов)")
        emb.add_field(name=".mine_info [участник сервера]", value="выводит кол-во намайненых монет участника")
        emb.add_field(name=".miningvivod <монеты>", value="выводит монеты с майнинга на баланс (комиссия 5%)")
        emb.add_field(name=".stavka <монеты>", value="вы ставите монеты(принцип как в казино)")
        emb.add_field(name=".top", value="выводит топ участников по монетам")
        emb.add_field(name=".usercard [участник сервера]", value="выводит карточку участника")
    await ctx.send(embed=emb)


@bot.command()
async def moder_roles(ctx, roles: commands.Greedy[discord.Role]):
    global conn, cursor
    roles_ides = []
    for role in roles:
        roles_ides.append(str(role.id))
    print(roles_ides)
    cursor.execute("UPDATE guilds SET moder_roles = %s WHERE guild_id = %s;", [roles_ides, str(ctx.guild.id)])
    conn.commit()

token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
