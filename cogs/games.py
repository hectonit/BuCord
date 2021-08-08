"""code of different games"""

import asyncio
import random

import discord
from discord.ext import commands, tasks

import configs
from configs import constants


class Tictactoe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def insert_table(table, ind, s):
        indexes = [0, 16, 20, 24, 44, 48, 52, 72, 76, 80]
        return table[:indexes[ind]] + s + table[indexes[ind] + 1:]

    @staticmethod
    def is_win(checked, situation):
        s = 3 - (len(situation) % 2 + 1)
        if (checked[1] == checked[2] == checked[3] == s) or (checked[4] == checked[5] == checked[6] == s) or (checked[7] == checked[8] == checked[9] == s) or (checked[1] == checked[4] == checked[7] == s) or (checked[2] == checked[5] == checked[8] == s) or (checked[3] == checked[6] == checked[9] == s) or (checked[1] == checked[5] == checked[9] == s) or (checked[3] == checked[5] == checked[7] == s):
            return s
        elif all(checked[1:]):
            return 3
        else:
            return 0

    @staticmethod
    def precalc(difficulty, situation, checked):
        res = Tictactoe.is_win(checked, situation)

        precalced = {situation: {"win": res, "step": 0}}
        if res == 1:
            return precalced, 10
        if res == 2:
            return precalced, -10
        if res == 3:
            return precalced, 0

        ranks_win = []
        ranks_lose = []
        ranks_draw = []

        for i in range(1, 10):
            if not checked[i]:
                checked[i] = len(situation) % 2 + 1
                p, rank = Tictactoe.precalc(
                    difficulty, situation + str(i), checked)
                checked[i] = 0
                precalced.update(p)

                if rank == 10:
                    ranks_win.append((10, i))
                elif rank == -10:
                    ranks_lose.append((-10, i))
                else:
                    ranks_draw.append((0, i))

        if len(situation) % 2:
            precalced[situation]["step"] = min(
                ranks_win + ranks_draw + ranks_lose)[1]
            return precalced, min(ranks_win + ranks_draw + ranks_lose)[0]
        if difficulty == "medium":
            rand = ranks_draw + ranks_win
            if not rand:
                rand += ranks_lose
        elif difficulty == "easy":
            rand = ranks_draw + ranks_lose + ranks_win
        else:
            precalced[situation]["step"] = max(
                ranks_win + ranks_draw + ranks_lose)[1]
            return precalced, max(ranks_win + ranks_draw + ranks_lose)[0]

        res = random.choice(rand)
        precalced[situation]["step"] = res[1]
        return precalced, res[0]

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
        pole = [0] * 10
        precalced, _rank = self.precalc(difficulty, situation, pole)
        count = 0
        table = constants.table

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
            emb.set_footer(text="отправьте нужную цифру в течении 60 секунд")
            await ctx.send(embed=emb)

            def check(m):
                text = m.content
                return text.isalnum() and len(text) == 1 and int(text) != 0 and not pole[int(text)] and ctx.author == m.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(ctx.author.mention + " время вышло!")
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
    bot.add_cog(Tictactoe(bot))
    print("Games finished")
