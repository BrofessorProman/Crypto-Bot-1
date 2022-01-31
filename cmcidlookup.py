import json, datetime, pickle, sqlite3

# todo - need to determine if there are multiple of the same symbols and ask the user via reactions which one they want

# Search through the list from CMC to see if the users request exists; return "error" if it was bad input or symbol doesn't exist
def cmcIDLookUp(message, session):
# Check to see when the list was last updated in the last day; if not fetch an updated map
  global day
  # Initialize a date object to represent the current day
  day = datetime.datetime.now(datetime.timezone.utc).day

  if day != datetime.datetime.now(datetime.timezone.utc).day:
    mapCMC(session)
    day = datetime.datetime.now(datetime.timezone.utc).day

  map_list = readCMCdb()

  if len(map_list) > 4:
    # todo - ask the user which crypto they wants as there are duplicates
  else:
    cmc_id = map_list[0]

  return cmc_id


# Take data from CMC and format it into a new dictionary (Format: {"crypto_ticker": {"id": cmc_id, "name": "crypto_name", "symbol": "crypto_ticker", "is_active": Bool}}), then pickle it to a file
def cleanMap(map_data):
  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  cursor.execute("""CREATE TABLE IF NOT EXISTS
      cmc_map(cmc_id INTEGER PRIMARY KEY, name TEXT, symbol TEXT, is_active INTEGER)""")

# Grab the "id," "name," "symbol" and "is_active" values from the map_data dictionary
  for i in range(len(map_data)):
    cmc_id = map_data[i]["id"]
    cmc_name = map_data[i]["name"]
    cmc_symbol = map_data[i]["symbol"]
    cmc_is_active = map_data[i]["is_active"]
    cursor.execute("""INSERT INTO cmc_datas VALUES (?, ?, ?, ?)""", (cmc_id, cmc_name, cmc_symbol, cmc_is_active))

  conn.commit()
  conn.close()

# Parse the ticker from the discord message
def getSymbolFromMessage(message):
  # todo - rework for sql
  split_list = message.split(" ", 1)
  symbol = split_list[1].upper()

  return symbol

# Get a map of CMC and return a list of all the items
def mapCMC(session):
  url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
  cmc_map = session.get(url)
  cmc_map_data = json.loads(cmc_map.text)
  cmc_map_list = cmc_map_data["data"]

  # Clean up the list returned from CMC and write it out to a .txt file
  cleanMap(cmc_map_list)

# Read from "CMC_Clean_Map.txt" return a dictionary
def readCMCdb(ticker):
  conn = sqlite3.connect("cmc_data.db")
  cursor = conn.cursor()

  cursor.execute("""SELECT * FROM cmc_maps WHERE name = ?""", (ticker))

  map_data = cursor.fetchall()
  conn.close()

  return map_data