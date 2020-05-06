import discord
from discord.ext import commands
import random
import os
import asyncio

bot = commands.Bot(command_prefix='$')
client = discord.Client()

finance = {}
profile = {}


@client.event
async def on_message(ctx):
    if profile.get(ctx.author.id) == None:
        profile[ctx.author.id] = [0, 0]
    else:
        profile[ctx.author.id][0] += 1
        if profile[ctx.author.id][0] >= 100:
            profile[ctx.author.id][1] += 1
    if finance.get(ctx.author.id) == None:
        finance[ctx.author.id] = 2
    else:
        finance[ctx.author.id] += 1


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def stavka(ctx, arg):
    if profile.get(ctx.author.id) == None:
        profile[ctx.author.id] = [0, 0]
    arg = int(arg)
    if arg > finance[ctx.author.id] or arg <= 0:
        await ctx.send("Число введено неверно.")
    else:
        multi = random.randint(0, 20) / 10
        finalresult = int(arg * multi)
        finance[ctx.author.id] -= arg
        finance[ctx.author.id] += finalresult
        await ctx.send("@{}, вы выиграли {} монет".format(ctx.author, finalresult))


@bot.command()
async def balans(ctx):
    if finance.get(ctx.author.id) == None:
        finance[ctx.author.id] = 2
    await ctx.send("@{}, ваш баланс: {}".format(ctx.author, finance[ctx.author.id]))


@bot.command()
async def profiler(ctx):
    if profile.get(ctx.author.id) == None:
        profile[ctx.author.id] = [0, 0]
    print(ctx.author.id)
    await ctx.send(
        "@{}, ваши очки: {}, уровень: {}".format(ctx.author, profile[ctx.author.id][0],
                                                 profile[ctx.author.id][1]))


@bot.command()
async def top(ctx):
    torr = list(finance.values())
    torr.sort()
    torr = torr[len(torr) - 5:]
    ind1 = "Нет информации"
    ind2 = "Нет информации"
    ind3 = "Нет информации"
    ind4 = "Нет информации"
    ind5 = "Нет информации"
    for k, v in finance.items():
        if v in torr and torr.index(v) == 0:
            ind1 = ("Первое место - {} - {}".format(bot.get_user(k), finance[k]))
        elif v in torr and torr.index(v) == 1:
            ind2 = ("Второе место - {} - {}".format(bot.get_user(k), finance[k]))
        elif v in torr and torr.index(v) == 2:
            ind3 = ("Третье место - {} - {}".format(bot.get_user(k), finance[k]))
        elif v in torr and torr.index(v) == 3:
            ind4 = ("Четвертое место - {} - {}".format(bot.get_user(k), finance[k]))
        elif v in torr and torr.index(v) == 4:
            ind5 = ("Пятое место - {} - {}".format(bot.get_user(k), finance[k]))
    await ctx.send("{}\n{}\n{}\n{}\n{}".format(ind1, ind2, ind3, ind4, ind5))


token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
