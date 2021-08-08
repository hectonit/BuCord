import discord
import redis
import asyncpg

from configs.constants import ONE_DAY
from .utils import connect, redis_connect

redis_con = redis_connect()

member_keys = ("user_id", "guild_id", "money", "points")
guild_keys = ("prefix", "guild_id", "goodbye", "welcome")


def to_dict(record):
    if not record:
        return None
    new_record = {}
    for field, value in record.items():
        new_record[field] = value
    return new_record


def get_member_cache(member_id, guild_id):
    name = str(member_id) + "_" + str(guild_id)
    record = {}
    for key in member_keys:
        res = redis_con.get(name + key)
        if res:
            record[key] = int(res.decode("utf-8"))
        else:
            return None
    return record


def get_guild_cache(guild_id):
    name = str(guild_id)
    record = {}
    for key in guild_keys:
        res = redis_con.get(name + key)
        if res:
            if key == "guild_id":
                res = int(res.decode("utf-8"))
            else:
                res = res.decode("utf-8")
            record[key] = res
        else:
            return None
    return record


def set_member_cache(member_id, guild_id, record):
    name = str(member_id) + "_" + str(guild_id)
    for key in member_keys:
        redis_con.set(name + key, record[key], ONE_DAY)


def set_guild_cache(guild_id, record):
    name = str(guild_id)
    for key in guild_keys:
        redis_con.set(name + key, record[key], ONE_DAY)


def delete_member_cache(member_id, guild_id):
    name = str(member_id) + "_" + str(guild_id)
    for key in member_keys:
        redis_con.delete(name + key)


def delete_guild_cache(guild_id):
    name = str(guild_id)
    for key in guild_keys:
        redis_con.delete(name + key)


async def get_member_info(member_id, guild_id):
    cache = get_member_cache(member_id, guild_id)
    if cache:
        return cache
    con = await connect()
    record = await con.fetchrow(
        "select * from users where user_id = $1 and guild_id = $2;", member_id, guild_id)
    if record:
        set_member_cache(member_id, guild_id, record)
    await con.close()
    return to_dict(record)


async def get_guild_info(guild_id):
    cache = get_guild_cache(guild_id)
    if cache:
        return cache
    con = await connect()
    record = await con.fetchrow(
        "select * from guilds where guild_id = $1;", guild_id)
    if record:
        set_guild_cache(guild_id, record)
    await con.close()
    return to_dict(record)


async def update_member(member_id, guild_id, new_record):
    set_member_cache(member_id, guild_id, new_record)
    con = await connect()
    await con.execute("update users set money = $1, points = $2 where user_id = $3 and guild_id = $4;",
                      new_record["money"], new_record["points"], member_id, guild_id)
    await con.close()


async def update_guild(guild_id, new_record):
    set_guild_cache(guild_id, new_record)
    con = await connect()
    await con.execute("update guilds set goodbye = $1, welcome = $2, prefix = $3 where guild_id = $4;",
                      new_record["goodbye"], new_record["welcome"], new_record["prefix"], guild_id)
    await con.close()


async def delete_member(member_id, guild_id):
    delete_member_cache(member_id, guild_id)
    con = await connect()
    await con.execute("delete from users where user_id = $1 and guild_id = $2;", member_id, guild_id)
    await con.close()


async def delete_guild(guild_id):
    delete_guild_cache(guild_id)
    con = await connect()
    await con.execute("delete from guilds where guild_id = $1;", guild_id)
    await con.close()


async def create_member(member_id, guild_id):
    record = {"user_id": member_id,
              "guild_id": guild_id, "money": 5, "points": 0}
    set_member_cache(member_id, guild_id, record)
    con = await connect()
    await con.execute("insert into users (user_id, guild_id) values ($1, $2);", member_id, guild_id)
    await con.close()


async def create_guild(guild_id):
    record = {"prefix": ".", "welcome": "Здарова!",
              "goodbye": "Прощай", "guild_id": guild_id}
    set_guild_cache(guild_id, record)
    con = await connect()
    await con.execute("insert into guilds (guild_id) values ($1);", guild_id)
    await con.close()


async def get_all_members():
    con = await connect()
    records = await con.fetch("select * from users;")
    await con.close()
    return records


async def get_all_members_ordered(guild_id):
    con = await connect()
    records = await con.fetch(
        "SELECT user_id, money FROM users WHERE guild_id = $1 ORDER BY money DESC;", guild_id)
    return records
