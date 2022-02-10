import time, json, sqlite3, cmcidlookup

# Initialize a time object to be used for updating the quotes table
time_sec = time.time()

# Fetch the top 100 crypto quotes from Coin Market Cap
def fetchQuotes(session):
  # Use this url to request ALL crypto quote data
  CMC_QUOTES_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

  quotes_data = session.get(CMC_QUOTES_URL)
  quotes_dict = json.loads(quotes_data.text)

  printCredits(quotes_dict)
  return quotes_dict

# Print the current credit count to the console after ever API request
def printCredits(quotes_dict):
  credits_used = quotes_dict["status"]["credit_count"]
  # todo - credits don't seem to be adding up; investigate why
  credits_remaining = (quotes_dict["status"]["total_count"]) - credits_used

  print(f"Credits used: {str(credits_used)}")
  print(f"Credits remaining: {str(credits_remaining)}")

# todo - dispatch this function on another thread so the user doesn't have to wait for this to finish
# Create and dump all the quote data returned from CMC into a database table
def writeQuotes(session):
    print("Building CMC Quotes table...")

    quotes_dict = fetchQuotes(session)
    conn = sqlite3.connect("cmc_data.db")
    cursor = conn.cursor()

  # Create a new table in cmc_data.db called cmc_quotes to dump all the crypto data returned from CMC into
    cursor.execute("""CREATE TABLE IF NOT EXISTS cmc_quotes 
        (cmc_id INTEGER,
        name TEXT,
        ticker TEXT,
        max_supply INTEGER,
        circulating_supply INTEGER,
        total_supply INTEGER,
        rank INTEGER,
        quote REAL,
        volume_24h INTEGER,
        volume_change_24h INTEGER,
        percent_change_1h REAL,
        percent_change_24h REAL,
        percent_change_7d REAL,
        percent_change_30d REAL,
        percent_change_60d REAL,
        percent_change_90d REAL,
        market_cap REAL,
        market_cap_dominance REAL,
        fully_diluted_market_cap REAL, FOREIGN KEY(cmc_id) REFERENCES cmc_map(cmc_id))""")

    for i in range(len(quotes_dict["data"])):
        quote_tuple = parseQuoteData(quotes_dict, i)

        cursor.execute("INSERT INTO cmc_quotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   quote_tuple)
        conn.commit()
    conn.close()

# Get the user requested quote either from the database or fetch new data if it's 60 seconds or older
def getQuote(session, ticker, cl_ctx):
    global time_sec

    if time.time() > (time_sec + 60):
        print("Fetching quotes...")
        fetchQuotes(session)
        time_sec = time.time()

    cmc_id = cmcidlookup.cmcIDLookUp(ticker, session, cl_ctx)

    # Check to see if there was anything returned
    if cmc_id is None:
        return

    conn = sqlite3.connect("cmc_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cmc_quotes WHERE cmc_id = ?", (cmc_id[0],))

    # If the crypto requested by the user isn't in the database, fetch quote data just for the crytpo
    try:
        db_list = cursor.fetchall()[0]
        # Full name of crypto
        crypto_name = db_list[1]
        # Quote
        price = formatQuote(db_list[7])
    except IndexError as e:
        print(f"Error: {e}")
        crypto_name, price = getIndividualQuote(cmc_id[0], session)

    conn.close()

    return crypto_name, price

# Format the price so that it reads out to the nearest penny if the price is > $1 otherwise format to 8 decimal places
def formatQuote(quote):
  if quote >= 1:
    price = "${:.2f}".format(quote)
  else:
    price = "${:.8f}".format(quote)

  return price

# If getQuotes() can't find the price, lookup the CMC id and grab that specific data
def getIndividualQuote(cmc_id, session):
  CMC_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?&id="

  response = session.get(CMC_url + str(cmc_id))
  data = json.loads(response.text)
  
  crypto_name = data["data"][str(cmc_id)]["name"]
  formated_price = formatQuote(data["data"][str(cmc_id)]["quote"]["USD"]["price"])

  return crypto_name, formated_price

# Udate the quote table in the database
def updateQuotes(session):
    print("Updating CMC Quotes table...")

    quotes_dict = fetchQuotes(session)

    conn = sqlite3.connect("cmc_data.db")
    cursor = conn.cursor()
    for i in range(len(quotes_dict["data"])):
        quote_tuple = parseQuoteData(quotes_dict, i)
        cursor.execute("""UPDATE cmc_quotes SET 
          name = ?,
          ticker = ?,
          max_supply = ?,
          circulating_supply = ?,
          total_supply = ?,
          rank = ?,
          quote = ?,
          volume_24h = ?,
          volume_change_24h = ?,
          percent_change_1h = ?,
          percent_change_24h = ?,
          percent_change_7d = ?,
          percent_change_30d = ?,
          percent_change_60d = ?,
          percent_change_90d = ?,
          market_cap = ?,
          market_cap_dominance = ?,
          fully_diluted_market_cap = ?
          WHERE cmc_id = ?""", quote_tuple)
        conn.commit()
    conn.close()

# Moved this to it's own function as both updateQuotes and writeQuotes use similar formats
def parseQuoteData(quotes_dict, index):
    conn = sqlite3.connect("cmc_data.db")
    cursor = conn.cursor()

    # Check to see if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'cmc_quotes'")

    list_to_tuple = [quotes_dict["data"][index]["name"],
                     quotes_dict["data"][index]["symbol"],
                     quotes_dict["data"][index]["max_supply"],
                     quotes_dict["data"][index]["circulating_supply"],
                     quotes_dict["data"][index]["total_supply"],
                     quotes_dict["data"][index]["cmc_rank"],
                     quotes_dict["data"][index]["quote"]["USD"]["price"],
                     quotes_dict["data"][index]["quote"]["USD"]["volume_24h"],
                     quotes_dict["data"][index]["quote"]["USD"]["volume_change_24h"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_1h"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_24h"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_7d"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_30d"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_60d"],
                     quotes_dict["data"][index]["quote"]["USD"]["percent_change_90d"],
                     quotes_dict["data"][index]["quote"]["USD"]["market_cap"],
                     quotes_dict["data"][index]["quote"]["USD"]["market_cap_dominance"],
                     quotes_dict["data"][index]["quote"]["USD"]["fully_diluted_market_cap"]]

    # If the table doesn't exist, add the cmc_id to the beginning of the list, else add it to the end when updating
    if len(cursor.fetchall()) == 0:
        list_to_tuple.insert(0, quotes_dict["data"][index]["id"])
    else:
        list_to_tuple.append(quotes_dict["data"][index]["id"])

    conn.close()

    return tuple(list_to_tuple)