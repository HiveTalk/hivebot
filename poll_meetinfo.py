import requests
import json
import logging
import asyncio
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from nostr_sdk import Keys, Client, NostrSigner, EventBuilder, init_logger, LogLevel

# Load environment variables from a .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(filename='meetinfo.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Fetch Nostr private key from environment variable
HIVE_API_KEY = os.getenv('HIVE_API_KEY')
if not HIVE_API_KEY:
    raise ValueError("The HIVE_API_KEY environment variable is not set.")

PRIVATE_KEY_HEX = os.getenv('NOSTR_PRIVATE_KEY_HEX')
if not PRIVATE_KEY_HEX:
    raise ValueError("The NOSTR_PRIVATE_KEY_HEX environment variable is not set.")


# Set up headers for authorization
headers = {
    'authorization': HIVE_API_KEY
}

# Initialize Nostr keys and signer
keys = Keys.parse(PRIVATE_KEY_HEX)
signer = NostrSigner.keys(keys)

# List of Nostr relay URLs
# NOSTR_RELAY_URLS = [
#     'wss://testnet.plebnet.dev/nostrrelay/1',
#     'wss://hivetalk.nostr1.com'
# ]

async def main():
    # Init logger
    init_logger(LogLevel.INFO)

    # Initialize client with signer
    client = Client(signer)

    # Add relays and connect
    await client.add_relay("wss://hivetalk.nostr1.com")
    await client.connect()

    url = "https://hivetalk.org/api/v1/meetinfo"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
#        logging.info("meetinfo data:")
#        logging.info(data)

        if "meetings" in data:
            for meeting in data["meetings"]:
                room_id = meeting["roomId"]
                peers = meeting["peers"]
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
                message = f"There are {peers} bee(s) now chatting in {room_id} on #HiveTalk, as of {current_time}. Join them now: https://hivetalk.org/join/{room_id} #grownostr"
                print(message)

                # Check if the roomId has been announced in the last hour
                if not was_announced_recently(room_id):
                    # Log the message
                    logging.info(message)
                    
                    # Post the message to Nostr relays
                    await post_to_nostr(client, message)

        else:
            logging.info("No meetings found.")

    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")

def was_announced_recently(room_id):
    with open('meetinfo.log', 'r') as log_file:
        now = datetime.now()
        for line in log_file:
            if room_id in line:
                log_time_str = line.split(' - ')[0]
                log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                if now - log_time < timedelta(hours=1):
                    return True
    return False

async def post_to_nostr(client, message):
    builder = EventBuilder.text_note(message, [])
    await client.send_event_builder(builder)

if __name__ == "__main__":
    asyncio.run(main())
