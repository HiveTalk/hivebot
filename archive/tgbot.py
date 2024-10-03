from telethon import TelegramClient, events
import os
import logging
import requests
import aiocron
from fetchdata import get_meetinfo
from dotenv import load_dotenv
# import yaml
# import json
load_dotenv()

base_url = "https://hivetalk.org/api/v1"

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

bot_commands = ["<b>/active</b> - List active meetings\n",
                "<b>/meeting</b> - Create a new meeting\n",
                "<b>/help</b> - Show this help message\n"]
#                "<b>/token</b> - Create a custom join URL\n",
#                "<b>/join</b> - Join a meeting with custom settings\n",

cmds = "".join(bot_commands)
help_msg = "Here are the commands I currently support: \n\n" + cmds
intro = '<b>HiveTalk Bot</b>\n\n' + help_msg

@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def start(event):
    await event.reply('Hi! Go to /help for instructions')

@client.on(events.NewMessage(pattern='(?i)/help', forwards=False, outgoing=False))
async def helpme(event):
    await event.reply(intro)

@client.on(events.NewMessage(pattern='(?i)/meeting', forwards=False, outgoing=False))
async def create_meeting(event):
    meeting_name = event.raw_text.split(' ', 1)[1] if len(event.raw_text.split()) > 1 else ''
    url = base_url + '/meeting'
    headers = {'accept': 'application/json', 'authorization': hive_api_key}
    data = {'name': meeting_name}
    logging.info(data)
    response = requests.post(url, headers=headers, data=data, timeout=10)
    if response.status_code == 200:
        meeting_info = response.json()
        logging.info(meeting_info)
        await event.reply(f"Meeting created: {meeting_info['meeting']}")
    else:
        await event.reply("Failed to create meeting")


def format_meetings(meetings_data):
    formatted_message = "<b>Meetings Information</b>\n\n"
    for meeting in meetings_data['meetings']:
        formatted_message += f"<b>Room ID:</b> {meeting['roomId']}\n"
        for peer in meeting['peers']:
            formatted_message += (
                f"  - <b>Name:</b> {peer['name']}"
                f"   {'<b>Presenter:</b> Yes' if peer['presenter'] else ''}"
                f" \n"
              #  f"   <b>Npub:</b> {peer['npub']}\n"
            )
        formatted_message += "\n"
    return formatted_message


@client.on(events.NewMessage(pattern='(?i)/active', forwards=False, outgoing=False))
async def list_active_meetings(event):
    url = base_url + '/meetings'
    headers = {'accept': 'application/json', 'authorization': hive_api_key}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        meetings = response.json()
        logging.info(meetings)

        if len(meetings['meetings']) > 0:
            formatted_message = format_meetings(meetings)
            # await event.reply("Active meetings:\n")
            await event.reply(formatted_message)

        else:
            await event.reply("No active meetings")
    else:
        await event.reply("Failed to retrieve active meetings")


# TODO FIX THIS for custom params
# @client.on(events.NewMessage(pattern='(?i)/join', forwards=False, outgoing=False))
# async def join_meeting(event):
#     # Here you should ask the user for the parameters
#     # For simplicity, we use hardcoded values as a demo here
#     data = {
#         'room': 'test',
#         'roomPassword': False,
#         'name': 'hivetalksfu',
#         'audio': True,
#         'video': True,
#         'screen': True,
#         'hide': False,
#         'notify': True,
#         #'token': {
#             # 'username' : "username",
#             # 'password': "password",
#             # 'presenter': True,
#             # 'expire': "1h",
#         #},
#     }
#     url = base_url + '/join'
#     headers = {
#         'accept': 'application/json',
#         'authorization': hive_api_key,
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, json=data, timeout=10)
#     if response.status_code == 200:
#         join_info = response.json()
#         await event.reply(f"Join info: {join_info}")
#     else:
#         await event.reply("Failed to join meeting")



async def post_to_telegram_channel():
    message = await get_meetinfo()
    if message is not None:
        await client.send_message(channel_id, message)


@aiocron.crontab('*/5 * * * *')
async def cron_job():
    await post_to_telegram_channel()


if __name__ == "__main__":
    client.start(bot_token=bot_token)

    with client:
        logger.info('(Press Ctrl+C to stop this)')
        client.run_until_disconnected()
