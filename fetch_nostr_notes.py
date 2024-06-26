import asyncio
import websockets
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from a .env file if it exists
load_dotenv()

# Sample Nostr public key (for demonstration purposes only)
# PUBLIC_KEY = 'npub1s7t3z7p5examplepublickeyk3v89sywqyfyl'
PUBLIC_KEY = os.getenv('NOSTR_PUBLIC_KEY_HEX')

# Nostr relay URL
NOSTR_RELAY_URL = 'wss://testnet.plebnet.dev/nostrrelay/1'

async def fetch_notes():
    async with websockets.connect(NOSTR_RELAY_URL) as websocket:
        now = int(time.time())
        yesterday = now - 24 * 60 * 60
        
        # Create a filter for events from the last 24 hours by the specified public key
        filter = {
            "kinds": [1],
            "authors": [PUBLIC_KEY],
            "since": yesterday
        }

        # Request for events matching the filter
        request = ["REQ", "request_id", filter]
        await websocket.send(json.dumps(request))

        # Collect and pretty print the responses
        while True:
            response = await websocket.recv()
            event = json.loads(response)

            if event[0] == "EVENT":
                event_data = event[2]
                created_at = datetime.utcfromtimestamp(event_data["created_at"]).strftime('%Y-%m-%d %H:%M:%S')
                content = event_data["content"]
                print(f"Time: {created_at}, Content: {content}")

            # Break the loop if "EOSE" (End of Stored Events) message is received
            if event[0] == "EOSE":
                break

if __name__ == "__main__":
    asyncio.run(fetch_notes())
