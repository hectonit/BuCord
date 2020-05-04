import discord
import random
import os

finance = {}


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as  {0} !'.format(self.user))

    async def on_message(self, message):
        print('Message from  {0.author} :  {0.content} '.format(message))
        if finance.get(message.author.id) == None:
            finance[message.author.id] = 2
        if message.author == client.user:
            return
        finance[message.author.id] += 1
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
                await message.channel.send("{}, вы выиграли {} монет".format(message.author, finalresult))
        if message.content.startswith("$баланс"):
            await message.channel.send("Ваш баланс: {}".format(finance[message.author.id]))


client = MyClient()
token = os.environ.get('BOT_TOKEN')
client.run(token)
