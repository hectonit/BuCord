import discord
from discord.ext import commands
import random
import os
import asyncio

bot = commands.Bot(command_prefix='$')
client = discord.Client()

finance = {}
profile = {}
profilearr = [0, 0]



@client.event
async def on_message(ctx):
    if profile.get(ctx.author.id) == None:
        profile[ctx.author.id] = profilearr
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
        profile[ctx.author.id] = profilearr
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
        profile[ctx.author.id] = profilearr
    await ctx.send(
        "@{}, ваши очки: {}, уровень: {}".format(ctx.author, profile[ctx.author.id][0],
                                                 profile[ctx.author.id][1]))


token = os.environ.get('BOT_TOKEN')
bot.run(str(token))
