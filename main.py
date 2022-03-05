import os, cmcidlookup, cmcpricelookup, config
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from discord.ext import commands
from os.path import isfile

# todo - store and track the fear and greed index along with the price of BTC at that time
# Do some data manipulation with the data in the future

def main():
  config.init()

  bot = commands.Bot(command_prefix="!")

  # CMC payload (can't seem to get this payload to work)
  # payload = {
  #   "id": 1,
  #   "slug": "bitcoin",
  #   "symbol": "BTC"
  # }

  # Map CMC on startup and get a fresh copy of quotes; check to see if the database and the tables exist
  if not isfile(os.getcwd() + "\cmc_data.db"):
    cmcidlookup.mapCMC(config.session)
    cmcpricelookup.writeQuotes(config.session)
  else:
    cmcidlookup.updateMapdb(config.session)
    cmcpricelookup.updateQuotes(config.session)

  @bot.event
  async def on_ready():
      print(f"We have logged in as {bot.user}")

  # Load bot extensions into a list
  extensions = []

  for filename in os.listdir("./cogs"):
      if filename.endswith(".py"):
          extensions.append(f"cogs.{filename[:-3]}")

  # Load bot extensions into the bot
  for extension in extensions:
      bot.load_extension(extension)

  bot.run(os.environ['botToken'])

if __name__ == "__main__":
  main()
