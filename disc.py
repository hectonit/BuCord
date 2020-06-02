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
import nekos
from bs4 import BeautifulSoup as BS

bot = commands.Bot(command_prefix='.')
client = discord.Client()
bot.remove_command("help")

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

cursor = conn.cursor()

jackpot = 10000

dt = int(time.time())
dt = dt // 60

brawlplayers = {}

colors = [0xFF0000, 0x39d0d6, 0xff6699, 0x17f90f, 0x0f13f9, 0xdff90f, 0xff8100, 0x740001, 0x330066]


@bot.event
async def on_ready():
    print("Bot logged as {}".format(bot.user))
    await bot.change_presence(activity=discord.Game("Слежку за сервером BU TEAM"))


@bot.event
async def on_message(message):
    global dt, cursor, conn
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    newdt = int(time.time())
    newdt = newdt // 60
    if message.author.id == 706401122721595444:
        return
    cursor.execute("SELECT * FROM users WHERE user_id = '{}';".format(message.author.id))
    users = cursor.fetchall()
    if len(users) == 0:
        cursor.execute("INSERT INTO users (user_id,level,money,minemoney,points) VALUES ('{}',{},{},{},{});".format(
            message.author.id, 0, 5, 0, 0))
    conn.commit()
    if newdt > dt:
        cursor.execute("SELECT * FROM users;")
        otherides = cursor.fetchall()
        ides = []
        for elem in otherides:
            ides.append(elem[0])
        for id in ides:
            cursor.execute(
                "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(
                    message.author.id))
            minemoney = cursor.fetchall()
            minemoney = int(minemoney[0][3])
            minemoney = minemoney + newdt - dt
            cursor.execute("UPDATE users SET minemoney = {} WHERE user_id = '{}';".format(minemoney, id))
            conn.commit()
        dt = newdt
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(message.author.id))
    money = cursor.fetchall()
    money = int(money[0][2]) + 1
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(message.author.id))
    points = cursor.fetchall()
    points = int(points[0][4]) + 1
    cursor.execute(
        "SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(message.author.id))
    level = cursor.fetchall()
    level = level[0][1]
    if points >= 100:
        level += 1
        points -= 100
    cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}';".format(money, message.author.id))
    cursor.execute("UPDATE users SET points = {} WHERE user_id = '{}';".format(points, message.author.id))
    cursor.execute("UPDATE users SET level = {} WHERE user_id = '{}';".format(level, message.author.id))
    conn.commit()
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send('Команда не найдена')


@bot.event
async def on_command(ctx):
    global cursor, conn
    cursor.execute("SELECT * FROM users WHERE user_id = '{}';".format(ctx.author.id))
    users = cursor.fetchall()
    if len(users) == 0:
        cursor.execute("INSERT INTO users (user_id,level,money,minemoney,points) VALUES ('{}',{},{},{},{});".format(
            ctx.author.id, 0, 5, 0, 0))
        cursor.execute("SELECT * FROM users;")
    conn.commit()


# ready
@bot.command()
async def stavka(ctx, arg: int):
    global cursor, jackpot, colors, conn
    cursor.execute("SELECT * FROM users WHERE user_id = '{}';".format(ctx.author.id))
    userfinance = cursor.fetchall()
    arg = int(arg)
    if arg > userfinance[0][2] or arg <= 0:
        await ctx.send("❌Число введено неверно.")
    else:
        multi = random.randint(0, 20) / 10
        pot = random.randint(0, 100)
        finalresult = int(arg * multi)
        firstfinance = userfinance[0][2] - arg
        cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}';".format(firstfinance, ctx.author.id))
        jackpot += arg
        jackpot -= finalresult
        emb = discord.Embed(color=random.choice(colors))
        emb.title = ("Ставка: {}$\nМножитель: {}\nВыигрыш: {}$".format(arg, multi, finalresult))
        if pot == 5:
            jackpotfinance = jackpot + userfinance[0][2]
            cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}';".format(jackpotfinance, ctx.author.id))
            await ctx.send(
                "{}, поздравляем!Вы забрали джекпот!!!Он составлял {} монет!!!".format(ctx.author.mention, jackpot))
            jackpot = 10000
        else:
            lastfinance = finalresult + firstfinance
            cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}';".format(lastfinance, ctx.author.id))
            await ctx.send(embed=emb)
    conn.commit()


# ready
@bot.command()
async def balans(ctx, member: discord.Member = None):
    global colors, cursor
    if member == None:
        member = ctx.author
    emb = discord.Embed(color=random.choice(colors))
    cursor.execute("SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(member.id))
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
    cursor.execute("SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(member.id))
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
    cursor.execute("SELECT * FROM users ORDER BY money;")
    topp = cursor.fetchall()
    topp.reverse()
    print(topp)
    counter = 0
    for elem in topp:
        biggest = elem[2]
        bigkey = int(elem[0])
        torr.append([biggest, bigkey])
        if bot.get_user(torr[counter][1]) == None:
            torr.pop()
            continue
        counter += 1
    print(torr)
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


@bot.command(pass_context=True)
async def give(ctx, member: discord.Member, arg):
    rolarr = []
    for role in ctx.author.roles:
        rolarr.append(role.id)
    moder = 706208121487360030
    if moder not in rolarr:
        await ctx.channel.send("У вас недостаточно прав")
        return
    if finance.get(member.id) == None:
        finance[member.id] = int(arg)
        await ctx.channel.send("{} вам выдано {} монет".format(member.mention, arg))
        return
    arg = int(arg)
    finance[member.id] += arg
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
    cursor.execute("SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(member.id))
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3] + newdt - dt
    dt = newdt
    await ctx.channel.send("{} , вы намайнили {} монет.".format(member.mention, minefinance))


@bot.command()
async def miningvivod(ctx, arg):
    global conn, cursor
    arg = int(arg)
    cursor.execute("SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(ctx.author.id))
    print(arg)
    minefinance = cursor.fetchall()
    minefinance = minefinance[0][3]
    print(minefinance)
    cursor.execute("SELECT user_id,level,money,minemoney,points FROM users WHERE user_id = '{}';".format(ctx.author.id))
    finance = cursor.fetchall()
    finance = finance[0][2]
    print(finance)
    print(minefinance)
    if arg > minefinance:
        await ctx.send("Число введено неверно.")
    else:
        anoarg = arg
        arg = int(arg * 0.95)
        finance = finance + arg
        minefinance = minefinance - arg
        cursor.execute("UPDATE users SET minemoney = {} WHERE user_id = '{}';".format(minefinance, ctx.author.id))
        cursor.execute("UPDATE users SET money = {} WHERE user_id = '{}';".format(finance, ctx.author.id))
        await ctx.send("Вы успешно вывели {} монет".format(anoarg))


@bot.command()
async def dollar(ctx):
    r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    course = r.json()
    course = course['Valute']['USD']['Value']
    await ctx.send("Курс доллара: {} рублей".format(course))


@bot.command()
async def registr(ctx, usertag):
    global cursor, conn
    r = requests.get("https://www.starlist.pro/stats/profile/{}".format(usertag))
    html = BS(r.content, "html.parser")
    user = {}
    club = {}
    club["name"] = (html.select(".link"))[3].text
    user["name"] = (html.select(".display-4"))[0].text
    user["trophies"] = (html.select(".shadow-normal"))[22].text
    user["club"] = club
    brawlplayers[ctx.author.id] = user
    await ctx.send(
        "Вы успешно зарегистрировались на нашем сервере! Ваш никнейм в игре Brawl Stars: {}! Если это не так , то обратитесь за помощью к модераторам!".format(
            user["name"]))
    cursor.execute("UPDATE users SET brawlstatus = TRUE WHERE user_id = '{}'".format(ctx.author.id))
    conn.commit()


@bot.command()
async def brawltrophies(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if brawlplayers.get(member.id) == None:
        await ctx.send(
            "Пользователь {} еще не зарегистрировался! Чтобы зарегистрироваться прейдите в канал 'регистрация'!".format(
                member.mention))
    else:
        await ctx.send("У вас {} кубков в игре Brawl Stars".format(brawlplayers[member.id]["trophies"]))


@bot.command()
async def brawlclub(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if brawlplayers.get(member.id) == None:
        await ctx.send(
            "Пользователь {} еще не зарегистрировался! Чтобы зарегистрироваться прейдите в канал 'регистрация'!".format(
                member.mention))
    else:
        await ctx.send("gg")


@bot.command()
async def help(ctx, arg=None):
    global colors
    emb = discord.Embed(color=random.choice(colors))
    if arg == None:
        emb.title = "Команды бота BuCord:"
        emb.description = "<> - обязательный аргумент , [] - необязательный аргумент"
        emb.add_field(name=".help [команда]", value="выводит это сообщение")
        emb.add_field(name=".dollar", value="выводит курс доллара к рублю")
        emb.add_field(name=".jackpot_info", value="выводит кол-во монет , которое составляет джекпот")
        emb.add_field(name=".balans [участник сервера]", value="выводит баланс участника")
        emb.add_field(name=".brawlclub [участник сервера]", value="выводит клуб участника")
        emb.add_field(name=".brawltrophies [участник сервера]", value="выводит кубки участника")
        emb.add_field(name=".give <учатсник сервера> <монеты>",
                      value="добавляет участнику указанное кол-во монет(только для модераторов)")
        emb.add_field(name=".mine_info [участник сервера]", value="выводит кол-во намайненых монет участника")
        emb.add_field(name=".miningvivod <монеты>", value="выводит монеты с майнинга на баланс (комиссия 5%)")
        emb.add_field(name=".registr <тег в Brawl Stars>", value="регистрирует вас на сервере")
        emb.add_field(name=".stavka <монеты>", value="вы ставите монеты(принцип как в казино)")
        emb.add_field(name=".top", value="выводит топ участников по монетам")
        emb.add_field(name=".usercard [участник сервера]", value="выводит карточку участника")
    await ctx.send(embed=emb)


@bot.command()
async def nswf(ctx, arg):
    if ctx.channel.is_nsfw():
        emb = discord.Embed()
        url = "https://pixabay.com/api/?key=16846925-0ecded025c1045855fb11c1bc&q=nude+{}".format(arg)
        url = url.json()
        url = url["hits"]
        url = random.choice(url)
        url = url["imageURL"]
        emb.set_image(url=url)
        await (await ctx.send(embed=emb)).delete(delay=10)
    else:
        await ctx.send("Это не NSWF канал!")


@bot.command()
async def close(ctx):
    global conn
    conn.close()

token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
