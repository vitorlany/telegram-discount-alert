from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')

if not API_ID or not API_HASH:
    print("Error: Please set TG_API_ID and TG_API_HASH in your .env first.")
    exit(1)

with TelegramClient(StringSession(), int(API_ID), API_HASH) as client:
    print("\n--- YOUR STRING SESSION ---")
    print(client.session.save())
    print("---------------------------\n")
    print("Copy the long string above and set it as TG_STRING_SESSION in your environment variables.")
