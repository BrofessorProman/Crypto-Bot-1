import json, datetime, pickle

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

  map_dict = readCMCFile()

  if isinstance(map_dict, dict):
    return map_dict[message]["id"]
  else:
    return "error"


# Take data from CMC and format it into a new dictionary (Format: {"crypto_ticker": {"id": cmc_id, "name": "crypto_name", "symbol": "crypto_ticker", "is_active": Bool}}), then pickle it to a file
def cleanMap(map_data):
  clean_dict = {}
  sub_dict = {}
  for i in range(len(map_data)):
    sub_dict["id"] = map_data[i]["id"]
    sub_dict["name"] = map_data[i]["name"]
    sub_dict["symbol"] = map_data[i]["symbol"]
    if map_data[i]["is_active"] == 0:
      sub_dict["is_active"] = False
    else:
      sub_dict["is_active"] = True

    # Must insert "sub_dict" using .copy() otherwise it will insert an empty dictionary
    clean_dict[map_data[i]["symbol"]] = sub_dict.copy()
    sub_dict.clear()

  with open("CMC_Clean_Map.txt", "wb") as file:
    pickle.dump(clean_dict, file)

# Take the users input and split it after the space to get the requested lookup symbol
def getSymbolFromMessage(message):
  with open("CMC_Clean_Map.txt", "rb") as file:
    cmc_map = pickle.load(file)

  split_list = message.split(" ", 1)
  symbol = split_list[1].upper()

  if symbol in cmc_map:
    return symbol
  else:
    return "error"

# Get a map of CMC and return a list of all the items
def mapCMC(session):
  url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
  cmc_map = session.get(url)
  cmc_map_data = json.loads(cmc_map.text)
  cmc_map_list = cmc_map_data["data"]

  # Clean up the list returned from CMC and write it out to a .txt file
  cleanMap(cmc_map_list)

# Read from "CMC_Clean_Map.txt" return a dictionary
def readCMCFile():
  with open("CMC_Clean_Map.txt", "rb") as file:
    map_data = pickle.load(file)
  
  return map_data