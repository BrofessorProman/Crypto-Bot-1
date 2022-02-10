from discord.ext import commands
import config
import cmcpricelookup
# todo - add comments

# List of available emoji to print for a response from the user
emoji_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

class Reactions(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Called when the user clicks an emoji posted by the bot
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        # Ensure the bot doesn't react to itself
        if reaction.user_id != self.client.user.id:
            # Cycle through the emoji posted by the bot to see which one the user interacted with
            for emoji in config.emoji_list_temp:
                if str(reaction.emoji) == emoji:
                    channel = self.client.get_channel(reaction.channel_id)
                    message = await channel.fetch_message(reaction.message_id)
                    await message.delete()
                    crypto_name, quote = cmcpricelookup.getIndividualQuote(config.crypto_list_temp
                                                                           [emoji_list.index(emoji)][0], config.session)
                    await channel.send(f"{crypto_name} Price: {quote}")
                    config.crypto_list_temp.clear()
                    config.emoji_list_temp.clear()
                else:
                    # todo - Delete the reaction if it's not in config.emoji_list_temp
                    pass

# Called to ask the user which crypto they intended to loop up if there are multiple crypto with the same ticker
async def askUserSymbol(context, crypto_list):
    config.crypto_list_temp = crypto_list.copy()
    discord_message = f"There are {len(config.crypto_list_temp)} crypto with the symbol " \
                      f"{config.crypto_list_temp[0][2]}. Which are you trying to lookup?"
    i = 0
    # Print the full name of the available crypto for the ticker the user input
    for crypto in crypto_list:
        discord_message = discord_message + f"\n{emoji_list[i]}: {crypto[1]}"
        i += 1
    message = await context.send(discord_message)

    x = 0
    # Add emoji to the message starting with '0'
    while x < len(crypto_list):
        await message.add_reaction(emoji_list[x])
        config.emoji_list_temp.append(emoji_list[x])
        x += 1

def setup(client):
    client.add_cog(Reactions(client))