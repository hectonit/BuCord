import discord
from discord.ext import commands
import random
import os
import asyncio

bot = commands.Bot(command_prefix='$')
client = discord.Client()

finance = {}
profile = {}


@bot.event
async def on_message(message):
    if message.author.id == 706401122721595444:
        return
    if profile.get(message.author.id) == None:
        profile[message.author.id] = [0, 0]
    else:
        profile[message.author.id][0] += 1
        if profile[message.author.id][0] >= 100:
            profile[message.author.id][1] += 1
            profile[message.author.id][0] = 0
    if finance.get(message.author.id) == None:
        finance[message.author.id] = 2
    else:
        finance[message.author.id] += 1
    await bot.process_commands(message)


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def stavka(ctx, arg: int):
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
    torr = torr[::-1]
    ind1 = "Нет информации"
    ind2 = "Нет информации"
    ind3 = "Нет информации"
    ind4 = "Нет информации"
    ind5 = "Нет информации"
    for k, v in finance.items():
        print(k)
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


@bot.command(pass_context=True)
async def give(ctx, member: discord.Member, arg):
    rolarr = []
    for role in member.roles():
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


token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
