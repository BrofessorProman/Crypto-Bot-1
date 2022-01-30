import time, json, pickle
from cmcidlookup import cmcIDLookUp

time_sec = time.time()

# todo - Go out and grab all the prices of all the crypto and store in a file if the data is 60 seconds old to reduce API calls, otherwise read from file to lookup the crypto price
def fetchQuotes(session):
  # Use this url to request ALL crypto quote data
  CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

  quotes_data = session.get(CMC_QUOTES_URL)
  quotes_dict = json.loads(quotes_data.text)

  printCredits(quotes_dict)
  writeQuotes(quotes_dict)

# Print the current credit count to the console after ever API request
def printCredits(quotes_dict):
  credits_used = quotes_dict["status"]["credit_count"]
  # todo - credits don't seem to be adding up; investigate why
  credits_remaining = (quotes_dict["status"]["total_count"]) - credits_used

  print(f"Credits used: {str(credits_used)}")
  print(f"Credits remaining: {str(credits_remaining)}")

# todo - dispatch this function on another thread so the user doesn't have to wait for this to finish

# Format the dictionary (Format: {"cypto_ticker": {"id": CMC_id, "name": "crypto_name", "symbol": "crypto_ticker", "max_supply": supply_num, "circulating_supply": circ_supply_num, "total_supply": total_suppply_num, "cmc_rank": rank_num, "quote": quote_num, "volume_24h": volume_num, "volume_change_24h": vol_chang_num, "percent_change_1h": float, "percent_change_24h": float, "percent_change_7d": float, "percent_change_30d": float, "percent_change_60d": float, "percent_change_90d": float, "market_cap": market_cap_num, "market_cap_dominance": cap_dom_num, "fully_diluted_market_cap": dil_cap_num}}) and write it to a file
def writeQuotes(quotes_dict):
  sub_dict = {}
  crypto_data = {}

  for i in range(len(quotes_dict["data"])):
    sub_dict["id"] = quotes_dict["data"][i]["id"]
    sub_dict["name"] = quotes_dict["data"][i]["name"]
    sub_dict["symbol"] = quotes_dict["data"][i]["symbol"]
    sub_dict["max_supply"] = quotes_dict["data"][i]["max_supply"]
    sub_dict["circulating_supply"] = quotes_dict["data"][i]["circulating_supply"]
    sub_dict["total_supply"] = quotes_dict["data"][i]["total_supply"]
    sub_dict["cmc_rank"] = quotes_dict["data"][i]["cmc_rank"]
    sub_dict["quote"] = quotes_dict["data"][i]["quote"]["USD"]["price"]
    sub_dict["volume_24h"] = quotes_dict["data"][i]["quote"]["USD"]["volume_24h"]
    sub_dict["volume_change_24h"] = quotes_dict["data"][i]["quote"]["USD"]["volume_change_24h"]
    sub_dict["percent_change_1h"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_1h"]
    sub_dict["percent_change_24h"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_24h"]
    sub_dict["percent_change_7d"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_7d"]
    sub_dict["percent_change_30d"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_30d"]
    sub_dict["percent_change_60d"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_60d"]
    sub_dict["percent_change_90d"] = quotes_dict["data"][i]["quote"]["USD"]["percent_change_90d"]
    sub_dict["market_cap"] = quotes_dict["data"][i]["quote"]["USD"]["market_cap"]
    sub_dict["market_cap_dominance"] = quotes_dict["data"][i]["quote"]["USD"]["market_cap_dominance"]
    sub_dict["fully_diluted_market_cap"] = quotes_dict["data"][i]["quote"]["USD"]["fully_diluted_market_cap"]

    crypto_data[quotes_dict["data"][i]["symbol"]] = sub_dict.copy()
    sub_dict.clear()

  with open("CMC_Quotes.txt", "wb") as file:
    pickle.dump(crypto_data, file)

# Get the user requested quote either from file or fetch a new copy
# todo - write a try/exect error to catch exception "KeyError"
def getQuote(session, ticker):
  global time_sec

  if time.time() > (time_sec + 60):
    print("Fetching quotes...")
    fetchQuotes(session)
    time_sec = time.time()

  with open("CMC_Quotes.txt", "rb") as file:
    quotes = pickle.load(file)
  
  try:
    price = formatQuote(quotes[ticker]["quote"])
    crypto_name = quotes[ticker]["name"]
  except KeyError as e:
    print(f"Can not find {ticker} in file. Error: {e}")
    cmc_id = cmcIDLookUp(ticker, session)
    crypto_name, price = getIndividualQuote(cmc_id, session)
    
  return crypto_name, price

# Format the price so that it reads out to the nearest penny if the price is > $1 otherwise print the entire price
def formatQuote(quote):
  if quote >= 1:
    price = "${:.2f}".format(quote)
  else:
    price = "${:.8f}".format(quote)

  return price

# If getQuotes() can't find the price, lookup the CMC id and grab that specific data; it seems like CMC doesn't return ALL quotes for ALL crypto
def getIndividualQuote(cmc_id, session):
  CMC_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?&id="

  response = session.get(CMC_url + str(cmc_id))
  data = json.loads(response.text)
  
  crypto_name = data["data"][str(cmc_id)]["name"]
  formated_price = formatQuote(data["data"][str(cmc_id)]["quote"]["USD"]["price"])

  return crypto_name, formated_price