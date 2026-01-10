import os
import re
import yaml
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'discount_bot')

if not API_ID or not API_HASH:
    print("Error: TG_API_ID or TG_API_HASH not found in .env file.")
    exit(1)

# Load configuration
def load_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()
raw_channels = config.get('channels', [])
CHANNELS = []
for ch in raw_channels:
    if isinstance(ch, str) and (ch.startswith('-100') or ch.lstrip('-').isdigit()):
        try:
            CHANNELS.append(int(ch))
        except ValueError:
            CHANNELS.append(ch)
    else:
        CHANNELS.append(ch)

PRODUCTS = config.get('products', [])

# Create the client and start it
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

def check_match(text):
    """
    Checks if the message text matches any of the product regexes.
    Returns the matching product name matches, otherwise None.
    """
    if not text:
        return None
    
    for product in PRODUCTS:
        pattern = product['regex']
        # Case insensitive search
        if re.search(pattern, text, re.IGNORECASE):
            return product['name']
    return None

import aiohttp

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def send_via_bot(user_id, message):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': user_id,
        'text': message,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"Failed to send bot alert: {await resp.text()}")
        except Exception as e:
            print(f"Error sending bot alert: {e}")

@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    if not event.message.raw_text:
        return
    
    print(f"Message received in {event.chat_id}: {event.message.raw_text[:30]}...") # Debug print

    match_name = check_match(event.message.raw_text)
    if match_name:
        sender = await event.get_sender()
        chat = await event.get_chat()
        
        # Construct alert message
        alert_text = (
            f"**🚨 MATCH FOUND: {match_name}**\n\n"
            f"**Source:** {chat.title if chat else 'Unknown'}\n"
            f"**Link:** [Go to Message](https://t.me/c/{extract_channel_id(event.chat_id)}/{event.id})\n\n"
            f"**Message:**\n{event.message.raw_text[:200]}..."
        )
        
        # Send to Saved Messages (Me) - via Userbot (Silent)
        await client.send_message('me', alert_text, link_preview=False)
        print(f"Match found! Sent to Saved Messages.")

        # Send via Bot (Loud Notification)
        me = await client.get_me()
        if BOT_TOKEN:
            await send_via_bot(me.id, alert_text)
            print("Sent push notification via Bot.")
    else:
        print("No regex match.")

def extract_channel_id(chat_id):
    # Helper to format channel ID for links (removes -100 prefix if present)
    s_id = str(chat_id)
    if s_id.startswith('-100'):
        return s_id[4:]
    return s_id

async def main():
    print("Bot is running...")
    # Refresh dialogs cache to avoid "Cannot find entity" errors
    print("Refreshing dialogs list...")
    await client.get_dialogs()
    
    # Print loaded config for debugging
    print(f"Monitoring {len(CHANNELS)} channels.")
    print(f"Tracking {len(PRODUCTS)} products.")
    
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
