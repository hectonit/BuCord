"""code of different games"""
import asyncio
import random
import discord
from discord.ext import commands, tasks

import constraints


class Tictactoe(commands.Cog):
    """
    functions for tictactoe
    """
    def __init__(self, bot):
        self.bot = bot


    @staticmethod
    def insert_table(table, ind, s):
        if ind == 1:
            index = 16
        if ind == 2:
            index = 20
        if ind == 3:
            index = 24
        if ind == 4:
            index = 44
        if ind == 5:
            index = 48
        if ind == 6:
            index = 52
        if ind == 7:
            index = 72
        if ind == 8:
            index = 76
        if ind == 9:
            index = 80
        return table[:index] + s + table[index + 1:]


    @staticmethod
    def is_win(checked, situation):
        s = len(situation) % 2 + 1
        if (checked[1] == checked[2] == checked[3] == s) or (checked[4] == checked[5] == checked[6] == s) or (checked[7] == checked[8] == checked[9] == s) or (checked[1] == checked[4] == checked[7] == s) or (checked[2] == checked[5] == checked[8] == s) or (checked[3] == checked[6] == checked[9] == s) or (checked[1] == checked[5] == checked[9] == s) or (checked[3] == checked[5] == checked[7] == s):
           return s
        elif all(checked[1:]):
            return 3
        else:
            return 0

        
    @staticmethod
    def precalc(difficulty, situation, checked):
        precalced = {}
        res = Tictactoe.is_win(checked, situation)
        precalced[situation] = {}
        precalced[situation]["win"] = res
        precalced[situation]["step"] = 0
        if res == 1:
            return precalced, 10
        if res == 1:
            return precalced, -10
        if res == 3:
            return precalced, 0
        ranks = []
        for i in range(1, 10):
            if not checked[i]:
                checked[i] = len(situation) % 2 + 1
                situation += str(i)
                p, rank = Tictactoe.precalc(difficulty, situation, checked)
                checked[i] = 0
                situation = situation[:-1]
                precalced.update(p)
                ranks.append((rank, i))
        if difficulty == "easy" or difficulty == "medium":
            rand = random.choice(ranks)
            precalced[situation]["step"] = rand[1]
            return precalced, rand[0]
        precalced[situation]["step"] = max(ranks)[1]
        return precalced, max(ranks)[0]
        
        
    @commands.command()
    async def tictactoe(self, ctx, difficulty="medium"):
        """
        all interaction with user during playing
        """
        if difficulty != "medium" and difficulty != "easy" and difficulty != "hard":
            await ctx.send("Выберете нормальную сложность: `easy`, `medium` или `hard`")
            return
        await ctx.send("BuCord думает...")
        situation = "0"
        precalced, rank = self.precalc(difficulty, situation, [0] * 10)
        count = 0
        pole = [0] * 10
        table = constraints.table
        while not precalced[situation]["win"]:
            emb = discord.Embed(color=discord.Colour.random())
            if count % 2 == 1:
                count += 1
                await ctx.send("BuCord думает...")
                situation += str(precalced[situation]["step"])
                table = self.insert_table(table, int(situation[-1]), "O")
                pole[int(situation[-1])] = 1
                emb.title = "BuCord походил на " + str(situation[-1]) + "!"
                emb.description = "```\n" + table + "```"
                await ctx.send(embed=emb)
                continue
            count += 1
            emb.title = "Твой ход! Напиши цифру клетки которая свободна"
            emb.description = "```\n" + table + "```"
            emb.set_footer(text="отправьте нужную цифру в течении 30 секунд")
            await ctx.send(embed=emb)


            def check(m):
                return m.content.isalnum() and len(m.content) == 1 and 1 <= int(m.content) <= 9 and not pole[int(m.content)] and ctx.author == m.author and m.channel == ctx.channel


            try:
                msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(ctx.author.mention, "время вышло!")
                return
            await ctx.send("Ход принят!")
            table = self.insert_table(table, int(msg.content), "X")
            pole[int(msg.content)] = 1
            situation += msg.content
        emb = discord.Embed()
        if precalced[situation]["win"] == 1:
            await ctx.send("BuCord победил!")
        elif precalced[situation]["win"] == 2:
            await ctx.send(ctx.author.mention + " победил!")
        elif precalced[situation]["win"] == 3:
            await ctx.send("Ничья")


def setup(bot):
    """
    setup cog

    :param bot: discord bot
    :type bot: commands.Bot
    """
    bot.add_cog(Tictactoe(bot))
    print("Games finished")
