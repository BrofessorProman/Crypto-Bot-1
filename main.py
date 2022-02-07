import os, discord, json, cmcidlookup
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from cmcpricelookup import getQuote, updateQuotes, writeQuotes
# import schedule, threading
from os.path import isfile
from discord.ext import commands

# client = discord.Client()
CMC_KEY = os.environ['CMC_API_KEY']

bot = commands.Bot(command_prefix="!")

# CMC payload (can't seem to get this payload to work)
payload = {
  "id": 1,
  "slug": "bitcoin",
  "symbol": "BTC"
}

fng_url = "https://api.alternative.me/fng/?limit=10&format=json&date_format=us"

# CMC header parameter to open the connection
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': CMC_KEY,
}

# Create a new session to connect to CMC (Coin Market Cap)
session = Session()
session.headers.update(headers)

# Map CMC on startup and get a fresh copy of quotes; check to see if the database and the tables exist
if not isfile("cmc_data.db"):
  cmcidlookup.mapCMC(session)
  writeQuotes(session)
else:
  cmcidlookup.updateMapdb(session)
  updateQuotes(session)

# cmcidlookup.updateMapdb(session)
# writeQuotes(session)

# todo - Use multiprocessing to accomplish this
# def autoPostFNG():
#   while True:
#     fng_index = schedule.every().day.at("00:00").do(get_fgIndex)
#     schedule.every().day.at("00:00").do(await message.channel.send("Now: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"] + '\n' + "Last Updated: " + fng_index["timestamp"]))
#     print("Waiting for 00:00 UTC")
#     sleep(5)

# # todo - Automate this function so that it runs at 00:00 (12 A.M.) UTC
def get_fgIndex():
  try:
    response = Session().get(fng_url)
    json_data = json.loads(response.text)
    fng_list = json_data["data"]
    return fng_list
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
    return

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def fng(ctx):
  fng_json = get_fgIndex()
  if isinstance(fng_json, list):
    fng_index = fng_json[0]
    await ctx.send("Now: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"] + '\n' + "Last Updated: " + fng_index["timestamp"])
    await ctx.send("https://alternative.me/crypto/fear-and-greed-index.png")

  else:
    await ctx.send("Bad request")

@bot.command()
async def yfng(ctx):
  fng_json = get_fgIndex()
  if isinstance(fng_json, list):
    fng_index = fng_json[1]
    await ctx.send("Yesterday: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"])
  else:
    await ctx.send("Bad request")

@bot.command()
async def price(ctx, arg):
  requested_sym = cmcidlookup.getSymbolFromMessage(arg)
  try:
    if requested_sym == "error":
      print("error")
      await ctx.send("Check the spelling of the ticker you entered. If it is correct, try again later.")
    else:
      # Client and context (ctx) tuple
      cl_ctx = (bot, ctx)
      try:
        crypto_name, quote = getQuote(session, requested_sym, cl_ctx)
        await ctx.send(f"{crypto_name} Price: {quote}")
      except TypeError as e:
        print(f"Error: {e}")

  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
    await ctx.send(f"Error: {e}")

# Load bot extensions into a list
extensions = []

for filename in os.listdir("./cogs"):
  if filename.endswith(".py"):
    extensions.append(f"cogs.{filename[:-3]}")

# Load bot extensions into the bot
if __name__ == "__main__":
  for extension in extensions:
    bot.load_extension(extension)

bot.run(os.environ['botToken'])