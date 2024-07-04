import requests
import logging
from datetime import datetime, timedelta, timezone
import logging


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


async def get_meetinfo():
    url = "https://hivetalk.org/api/v1/meetinfo"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if "meetings" in data:
            for meeting in data["meetings"]:
                room_id = meeting["roomId"]
                peers = meeting["peers"]
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
                message = f"There are {peers} bee(s) now chatting in {room_id} on #HiveTalk, as of {current_time}. Join them now: https://hivetalk.org/join/{room_id}"
                
                print(message)

                # Check if the roomId has been announced in the last hour
                if not was_announced_recently(room_id):
                    # Log the message
                    logging.info(message)
                    
                    # Post the message to Nostr relays
                    return message
                else:
                    return None

        else:
            logging.info("No meetings found.")
            return None

    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")