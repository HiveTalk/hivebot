from telethon import TelegramClient, events
import os
import logging
from dotenv import load_dotenv
#import yaml
# import aiocron
import requests
# import json

load_dotenv()

api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
bot_token = os.getenv('BOT_TOKEN')  
channel_id = '@hivetalkchannel'
hive_api_key = os.getenv('HIVE_API_KEY')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)

client = TelegramClient('anon', api_id, api_hash)
client.parse_mode = 'html'

bot_commands = ["<b>/meeting</b> - Create a new meeting\n",
                "<b>/active</b> - List active meetings\n",
                "<b>/token</b> - Create a custom join URL\n",
                "<b>/join</b> - Join a meeting\n",
                "<b>/help</b> - Show this help message\n"]

cmds = "".join(bot_commands)
help_msg = "Here are the commands I currently support: \n\n" + cmds
intro = '<b>HiveTalk Bot</b>\n\n' + help_msg

@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def start(event):
    await event.reply('Hi! Go to /helpme for instructions')

@client.on(events.NewMessage(pattern='(?i)/help', forwards=False, outgoing=False))
async def helpme(event):
    await event.reply(intro)

@client.on(events.NewMessage(pattern='(?i)/meeting', forwards=False, outgoing=False))
async def create_meeting(event):
    ## custom meeting name doesn't work in api end point right now
    meeting_name = event.raw_text.split(' ', 1)[1] if len(event.raw_text.split()) > 1 else ''
    url = 'https://hivetalk.org/api/v1/meeting'
    headers = {'accept': 'application/json', 'authorization': hive_api_key}
    data = ''
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        meeting_info = response.json()
        await event.reply(f"Meeting created: {meeting_info['meeting']}")
    else:
        await event.reply("Failed to create meeting")

@client.on(events.NewMessage(pattern='(?i)/active', forwards=False, outgoing=False))
async def list_active_meetings(event):
    url = 'https://hivetalk.org/api/v1/meetings'
    headers = {'accept': 'application/json', 'authorization': hive_api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        meetings = response.json()
        logging.info(meetings)
        if len(meetings['meetings']) > 0:
            await event.reply("Active meetings:\n" + "\n".join(meetings))
        else:
            await event.reply("No active meetings")
    else:
        await event.reply("Failed to retrieve active meetings")

# TODO FIX THIS
@client.on(events.NewMessage(pattern='(?i)/token', forwards=False, outgoing=False))
async def create_token(event):
    # Here you should ask the user for username, password, presenter, and expiration
    # For simplicity, we use hardcoded values
    username = 'username'
    password = 'password'
    presenter = True
    expire = '1h'
    url = 'https://hivetalk.org/api/v1/token'
    headers = {
        'accept': 'application/json',
        'authorization': hive_api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'username': username,
        'password': password,
        'presenter': presenter,
        'expire': expire
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        token_info = response.json()
        await event.reply(f"Token created: {token_info}")
    else:
        await event.reply("Failed to create token")


# TODO FIX THIS for custom params
@client.on(events.NewMessage(pattern='(?i)/join', forwards=False, outgoing=False))
async def join_meeting(event):
    # Here you should ask the user for the parameters
    # For simplicity, we use hardcoded values
    data = {
        'room': 'test',
        'roomPassword': False,
        'name': 'hivetalksfu',
        'audio': False,
        'video': False,
        'screen': False,
        'hide': False,
        'notify': False,
        'token': {
            'username': 'username',
            'password': 'password',
            'presenter': True,
            'expire': '1h'
        }
    }
    url = 'https://hivetalk.org/api/v1/join'
    headers = {
        'accept': 'application/json',
        'authorization': hive_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        join_info = response.json()
        await event.reply(f"Join info: {join_info}")
    else:
        await event.reply("Failed to join meeting")


# TODO FIX THIS
# @aiocron.crontab('*/5 * * * *')
# async def post_to_telegram_channel():
#     async with TelegramClient('anon', api_id, api_hash) as client:
#         await client.start(bot_token=bot_token)
#         # Implement your get_meetinfo function
#         message = await get_meetinfo()
#         if message is not None:
#             await client.send_message(channel_id, message)

# async def get_meetinfo():
#     # Implement the logic to get meeting info
#     return "Meeting info message"

client.start(bot_token=bot_token)

with client:
    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
