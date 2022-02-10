from requests import Session
import os

# Initialize all variables that need to hold persistent data across files/instances

CMC_KEY = os.environ['CMC_API_KEY']

# CMC header parameter to open the connection
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': CMC_KEY,
}

def init():
    # Temp list used to store all crypto with the same ticker
    global crypto_list_temp
    crypto_list_temp = []

    # List used to store emoji added to message in discordreactions.askUserSymbol function
    global emoji_list_temp
    emoji_list_temp = []

    # Create a new session to connect to CMC (Coin Market Cap)
    global session
    session = Session()
    session.headers.update(headers)