import asyncio
import json, datetime, sqlite3
import cogs.discordreactions

# Search through the database to see if the users request exists; return "error" if it was bad input or symbol
# doesn't exist
def cmcIDLookUp(message, session, cl_ctx):
  # Check to see when the list was last updated in the last day; if not fetch an updated map
  global day
  # Initialize a date object to represent the current day
  day = datetime.datetime.now(datetime.timezone.utc).day

  if day != datetime.datetime.now(datetime.timezone.utc).day:
    fetchCMCMap(session)
    day = datetime.datetime.now(datetime.timezone.utc).day

  map_list = readCMCdb(message)

  # Check to see if the list has more than 1 item; more than 1 items means there are duplicate crypto
  # using the same ticker (SQL database will return a list of tuples if is more than one  crypto with the same ticker)
  if len(map_list) > 1:
    # Ask the user which crypto they had intended to lookup (cl_ctx[0] = client & cl_ctx[1] = context)
    asyncio.run_coroutine_threadsafe(cogs.discordreactions.askUserSymbol(cl_ctx[1], map_list), cl_ctx[0].loop)
    return
  else:
    cmc_id = map_list[0]
    return cmc_id

# Take data from CMC and dump into a database table; map all crypto from Coin Market Cap
def mapCMC(session):
  cmc_map_list = fetchCMCMap(session)
  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  print("Building CMC Map table...")

  cursor.execute("""CREATE TABLE IF NOT EXISTS
      cmc_map(cmc_id INTEGER PRIMARY KEY, name TEXT, symbol TEXT, is_active INTEGER)""")

  # Input the "id," "name," "symbol" and "is_active" values from the map_data dictionary into the cmc_map table
  for i in range(len(cmc_map_list)):
    cmc_id = cmc_map_list[i]["id"]
    cmc_name = cmc_map_list[i]["name"]
    cmc_symbol = cmc_map_list[i]["symbol"]
    cmc_is_active = cmc_map_list[i]["is_active"]
    cursor.execute("""INSERT INTO cmc_map VALUES (?, ?, ?, ?)""", (cmc_id, cmc_name, cmc_symbol, cmc_is_active))
    conn.commit()

  conn.close()

# Parse the ticker from the discord message and check to see if the ticker exists in the database
def getSymbolFromMessage(message):
  symbol = message.upper()

  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM cmc_map WHERE symbol = ?", (symbol,))

  # Check to see if the symbol exits in the database
  if (len(cursor.fetchall())) == 0:
    conn.close()
    return "error"
  else:
    conn.close()
    return symbol

# Fetch a map of CMC and return a list of all the items
def fetchCMCMap(session):
  url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
  cmc_map = session.get(url)
  cmc_map_data = json.loads(cmc_map.text)
  cmc_map_list = cmc_map_data["data"]

  return cmc_map_list

# Read the cmc_data database and return a list for a specific crypto or multiple lists if the ticker is not unique
def readCMCdb(ticker):
  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM cmc_map WHERE symbol = ?", (ticker,))

  map_data = cursor.fetchall()
  conn.close()

  return map_data

# Update the cmc_map table in the cmc_data.db
def updateMapdb(session):
  print("Updating CMC Map table...")

  cmc_map_list = fetchCMCMap(session)

  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  for i in range(len(cmc_map_list)):
    cmc_name = cmc_map_list[i]["name"]
    cmc_symbol = cmc_map_list[i]["symbol"]
    cmc_is_active = cmc_map_list[i]["is_active"]
    cursor.execute("UPDATE cmc_map SET name = ?, symbol = ?, is_active = ?", (cmc_name, cmc_symbol, cmc_is_active))

  conn.close()