from telethon import TelegramClient
import os
from fetchdata import get_meetinfo
from dotenv import load_dotenv

load_dotenv()

# Replace 'YOUR_API_ID' and 'YOUR_API_HASH' with your values from my.telegram.org
# Replace 'YOUR_BOT_TOKEN' with the token you got from the BotFather
# Use '@channelusername' or '-1001234567890' format

api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
bot_token = os.getenv('BOT_TOKEN')  
channel_id = '@hivetalkchannel'  
print('api_id: ', api_id)
print('api_hash: ', api_hash)
print('bot_token: ', bot_token)
print('channel_id: ', channel_id)

async def post_to_telegram_channel():
    async with TelegramClient('anon', api_id, api_hash) as client:
        await client.start(bot_token=bot_token)
        message = await get_meetinfo()
        if message is not None:
            await client.send_message(channel_id, message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(post_to_telegram_channel())
