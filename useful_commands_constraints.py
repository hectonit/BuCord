import discord
from discord.ext import commands


def is_moder():
    def predicate(ctx):
        return True if ctx.author.permissions.administrator else False

    return commands.check(predicate)


def show_real_nick(member: discord.Member):
    return member.display_name + "#" + member.discriminator
