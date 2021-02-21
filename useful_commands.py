"""module for some useful commands"""

import discord
import psycopg2

from constraints import DATABASE_URL
from instances import Cursor


def connect():
    """
    create db connection

    :return: connection
    :rtype: psycopg2.extensions.connection
    """
    con = psycopg2.connect(DATABASE_URL, cursor_factory=Cursor)
    con.autocommit = True
    return con


def show_real_nick(member: discord.Member):
    """
    shows real nick on guild with discriminator

    :param member: member of guild
    :type member: discord.Member
    :return: real nick
    :rtype: str
    """
    return member.display_name + "#" + member.discriminator
