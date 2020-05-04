import discord
import random
import os

finance = {}
profile = {}
profilearr = [0, 0]


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as  {0} !'.format(self.user))

    async def on_message(self, message):
        print('Message from  {0.author} :  {0.content} '.format(message))
        if finance.get(message.author.id) == None:
            finance[message.author.id] = 2
        if profile.get(message.author.id) == None:
            profile[message.author.id] = profilearr
        if message.author == client.user:
            return
        finance[message.author.id] += 1
        profile[message.author.id][0] += 1
        if profile[message.author.id][0] >= 100:
            profile[message.author.id][1] += 1
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')
        if message.content.startswith("$ставка"):
            arr = message.content.split()
            lol = arr[len(arr) - 1]
            if int(lol) > finance[message.author.id]:
                await message.channel.send("У вас недостаточно средств")
            else:
                multi = random.randint(0, 20) / 10
                finalresult = int(int(lol) * multi)
                finance[message.author.id] -= int(lol)
                finance[message.author.id] += finalresult
                await message.channel.send("@{}, вы выиграли {} монет".format(message.author, finalresult))
        if message.content.startswith("$баланс"):
            await message.channel.send("@{}, ваш баланс: {}".format(message.author, finance[message.author.id]))
        if message.content.startswith("$профиль"):
            await message.channel.send(
                "@{}, ваши очки: {}, уровень: {}".format(message.author, profile[message.author.id][0],
                                                         profile[message.author.id][1]))


client = MyClient()
token = os.environ.get('BOT_TOKEN')
client.run(str(token))
