import os, discord, json, cmcidlookup
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from cmcpricelookup import getQuote, updateQuotes, writeQuotes
# import schedule, threading
from os.path import isfile

client = discord.Client()
CMC_KEY = os.environ['CMC_API_KEY']

# url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

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

# todo - Automate this function so that it runs at 00:00 (12 A.M.) UTC
def get_fgIndex():
  try:
    response = Session().get(fng_url)
    json_data = json.loads(response.text)
    fng_list = json_data["data"]
    return fng_list
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
    return

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('!fng'):
    fng_json = get_fgIndex()
    if isinstance(fng_json, list):
      fng_index = fng_json[0]
      await message.channel.send("Now: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"] + '\n' + "Last Updated: " + fng_index["timestamp"])
      await message.channel.send("https://alternative.me/crypto/fear-and-greed-index.png")

    else:
      await message.channel.send("Bad request")
  elif message.content.startswith('!yfng'):
    fng_json = get_fgIndex()
    if isinstance(fng_json, list):
      fng_index = fng_json[1]
      await message.channel.send("Yesterday: " + fng_index["value_classification"] + '\n' + "FnG Index: " + fng_index["value"])
    else:
      await message.channel.send("Bad request")

  elif message.content.startswith("!price"):
    requested_sym = cmcidlookup.getSymbolFromMessage(message.content)
    try:
      if requested_sym == "error":
        print("error")
        await message.channel.send("Check the spelling of the ticker you entered. If it is correct, try again later.")
      else:
        crypto_name, quote = getQuote(session, requested_sym)

        await message.channel.send(f"{crypto_name} Price: {quote}")
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)
      await message.channel.send(f"Error: {e}")

client.run(os.environ['botToken'])