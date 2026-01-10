from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'discount_bot')

client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

async def main():
    print("Fetching your channels and groups...")
    # Iterate over all dialogs (chats)
    async for dialog in client.iter_dialogs():
        # Filter for Channels and Groups
        if dialog.is_channel or dialog.is_group:
            print(f"Name: {dialog.name} | ID: {dialog.id}")

with client:
    client.loop.run_until_complete(main())
