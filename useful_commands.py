"""module for some useful commands"""
import asyncio
import ssl

import asyncpg
import discord
from discord.ext import commands

from constraints import DATABASE_URL


def create_loop():
    """
    create db connection

    :return: connection
    :rtype: asyncpg.connection.Connection
    """
    async def create_connection():
        """
        asyncio loop for creating connection

        """
        global con
        ctx = ssl.create_default_context(cafile="")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        con = await asyncpg.connect(DATABASE_URL, ssl=ctx)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_connection())
    return con


def is_moder():
    """
    check for command, is member moderator or not

    :return: checker
    :rtype: Command
    """
    def predicate(ctx):
        """
        check administrator permission

        :param ctx: context
        :type ctx: discord.ext.commands.Context
        :return: True if administrator else False
        :rtype: bool
        """
        return True if ctx.author.permissions.administrator else False

    return commands.check(predicate)


def show_real_nick(member: discord.Member):
    """
    shows real nick on guild with discriminator

    :param member: member of guild
    :type member: discord.Member
    :return: real nick
    :rtype: str
    """
    return member.display_name + "#" + member.discriminator
