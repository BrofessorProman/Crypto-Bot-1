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

  # todo -  move the printing to a function as cogs.discordreations.on_raw_reaction_add uses the same print statement
  # Command to look up a crypto price based on a ticker
  @bot.command()
  async def price(ctx, arg):
      requested_sym = cmcidlookup.getSymbolFromMessage(arg)

      # Try to get the requested crypto quote
      try:
          if requested_sym == "error":
              print("error")
              await ctx.send("Check the spelling of the ticker you entered. If it is correct, try again later.")
          else:
              # Client and context (ctx) tuple
              cl_ctx = (bot, ctx)

              # Try statement for when multiple crypto share the same ticker; nothing is retuned in this case
              try:
                  crypto_name, quote = cmcpricelookup.getQuote(config.session, requested_sym, cl_ctx)
                  await ctx.send(f"{crypto_name} Price: {quote}")
              except TypeError as e:
                  print(f"Error: {e}")

      except (ConnectionError, Timeout, TooManyRedirects) as e:
          print(e)
          await ctx.send(f"Error: {e}")

  # @bot.command()
  # async def help(ctx):
  #   await ctx.send("W.I.P.")

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
