import discord
from discord.ext import commands

# todo - add comments

emoji_list = ["1️⃣", "2️⃣", "3️⃣"]

class Reactions(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.user_id != self.client.user.id:
            if str(reaction.emoji) == "1️⃣":
                channel = self.client.get_channel(reaction.channel_id)
                message = await channel.fetch_message(reaction.message_id)
                print("We have lift off!")
                # Do some stuff before the delete statement
                # todo - Grab last message, pull out the crypto name, lookup name in db, send id to cmc and return price
                await message.delete()

    @commands.command()
    async def test(self, context):
        message = await context.send(f"\n1️⃣: If you dislike Boe Jiden\n2️⃣: If you think he's a failed"
                                 f"president\n3️⃣: If you think he poops his pants.")
        for emoji in emoji_list:
            await message.add_reaction(emoji)

async def askUserSymbol(context, crypto_list):
    discord_message = f"There are {len(crypto_list)} crypto with the symbol {crypto_list[0][2]}. " \
                      f"Which are you trying to lookup?"
    i = 0
    for crypto in crypto_list:
        discord_message = discord_message + f"\n{emoji_list[i]}: {crypto[1]}"
        i += 1
    message = await context.send(discord_message)

    x = 0
    while x < len(crypto_list):
        await message.add_reaction(emoji_list[x])
        x += 1

def setup(client):
    client.add_cog(Reactions(client))