from discord.ext import commands
import config
import cmcpricelookup
# todo - add comments

emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

class Reactions(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.user_id != self.client.user.id:
            for emoji in config.emoji_list_temp:
                if str(reaction.emoji) == emoji:
                    channel = self.client.get_channel(reaction.channel_id)
                    message = await channel.fetch_message(reaction.message_id)
                    # Do some stuff before the delete statement
                    await message.delete()
                    crypto_name, quote = cmcpricelookup.getIndividualQuote(config.crypto_list_temp
                                                                           [emoji_list.index(emoji)][0], config.session)
                    await channel.send(f"{crypto_name} Price: {quote}")
                    config.crypto_list_temp.clear()
                    config.emoji_list_temp.clear()
                else:
                    # todo - Delete the reaction if it's not in config.emoji_list_temp
                    pass


    @commands.command()
    async def test(self, context):
        message = await context.send(f"\n1️⃣: If you dislike Boe Jiden\n2️⃣: If you think he's a failed"
                                 f"president\n3️⃣: If you think he poops his pants.")
        for emoji in emoji_list:
            await message.add_reaction(emoji)

async def askUserSymbol(context, crypto_list):
    config.crypto_list_temp = crypto_list.copy()
    discord_message = f"There are {len(config.crypto_list_temp)} crypto with the symbol " \
                      f"{config.crypto_list_temp[0][2]}. Which are you trying to lookup?"
    i = 0
    for crypto in crypto_list:
        discord_message = discord_message + f"\n{emoji_list[i]}: {crypto[1]}"
        i += 1
    message = await context.send(discord_message)

    x = 0
    while x < len(crypto_list):
        await message.add_reaction(emoji_list[x])
        config.emoji_list_temp.append(emoji_list[x])
        x += 1

def setup(client):
    client.add_cog(Reactions(client))