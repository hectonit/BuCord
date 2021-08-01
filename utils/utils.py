"""module for some utils"""

import discord
import psycopg2
import redis

import configs
import utils
from configs.constants import DATABASE_URL, REDIS_HOST, REDIS_PASS, REDIS_PORT
from utils.entities import Cursor


def connect():
    """
    create db connection

    :return: connection
    :rtype: psycopg2.extensions.connection
    """
    con = psycopg2.connect(DATABASE_URL, cursor_factory=Cursor)
    con.autocommit = True
    return con


def redis_connect():
    redis_con = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
    return redis_con


def show_real_nick(member: discord.Member):
    """
    shows real nick on guild with discriminator

    :param member: member of guild
    :type member: discord.Member
    :return: real nick
    :rtype: str
    """
    return member.display_name + "#" + member.discriminator
