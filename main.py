import os
import re
import yaml
import aiohttp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'discount_bot')
STRING_SESSION = os.getenv('TG_STRING_SESSION')

PRICE_REGEX = r'(?i)(?:(?:POR:|Valor:|💰|-)?\s*R\$\s*|(?:POR:|Valor:)\s*)(\d+(?:[.,]\d+)*)'

if not API_ID or not API_HASH:
    print("Error: TG_API_ID or TG_API_HASH not found in .env file.")
    exit(1)

# Load configuration
def load_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

def process_channels(raw_list):
    processed = []
    for ch in raw_list:
        if isinstance(ch, str) and (ch.startswith('-100') or ch.lstrip('-').isdigit()):
            try:
                processed.append(int(ch))
            except ValueError:
                processed.append(ch)
        else:
            processed.append(ch)
    return processed

PRODUCT_CHANNELS = process_channels(config.get('channels', []))
COUPON_CHANNELS = process_channels(config.get('coupon_channels', []))
# Combine lists, removing duplicates
ALL_CHANNELS = list(set(PRODUCT_CHANNELS + COUPON_CHANNELS))

PRODUCTS = config.get('products', [])
STORES = config.get('stores', [])

# Create the client and start it
if STRING_SESSION:
    print("Using session string from environment.")
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
else:
    print(f"Using session file: {SESSION_NAME}.session")
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
        if re.search(pattern, text, re.IGNORECASE):
            counter_pattern = product.get('counter_regex')
            if counter_pattern and re.search(counter_pattern, text, re.IGNORECASE):
                continue
            
            return product['name']
            return product['name']
    return None

def check_store_match(text):
    """
    Checks if the message text matches any of the store regexes.
    Returns the matching store name matches, otherwise None.
    """
    if not text:
        return None
    
    for store in STORES:
        pattern = store['regex']
        if re.search(pattern, text, re.IGNORECASE):
            return store['name']
    return None

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

@client.on(events.NewMessage(chats=ALL_CHANNELS))
async def handler(event):
    if not event.message.raw_text:
        return
    
    print(f"Message received in {event.chat_id}: {event.message.raw_text[:30]}...") # Debug print

    match_name = None
    
    # Check if message is from a product channel
    if event.chat_id in PRODUCT_CHANNELS:
        match_name = check_match(event.message.raw_text)
    
    # If no match yet (or not a product channel), check if it's a coupon channel
    if not match_name and event.chat_id in COUPON_CHANNELS:
        match_name = check_store_match(event.message.raw_text)

    if match_name:
        chat = await event.get_chat()
        chat_title = chat.title if chat else 'Unknown'
        msg_id = event.id
        channel_id = extract_channel_id(event.chat_id)
        msg_link = f"https://t.me/c/{channel_id}/{msg_id}"
        price_match = re.search(PRICE_REGEX, event.message.raw_text)
        product_price = price_match.group(1) if price_match else None

        template = config.get('alert_template', 
            "**🚨 MATCH FOUND: {product_name}**\n\n"
            "**Price:** {product_price}\n"
            "**Source:** {chat_title}\n"
            "**Link:** [Go to Message]({message_link})\n\n"
            "**Message:**\n{message_text}"
        )

        # Format alert message
        try:
            alert_text = template.format(
                product_name=match_name,
                product_price=product_price,
                chat_title=chat_title,
                message_link=msg_link,
                message_text=event.message.raw_text[:500] + ("..." if len(event.message.raw_text) > 500 else "")
            )
        except Exception as e:
            print(f"Error formatting template: {e}. Using fallback.")
            alert_text = f"Match: {match_name}\nPrice: {product_price}\nLink: {msg_link}"

        # Send via Bot (Loud Notification)
        me = await client.get_me()
        if BOT_TOKEN:
            await send_via_bot(me.id, alert_text)
            print(f"Match found! Sent push notification via Bot for {match_name}.")
        else:
            print(f"Match found! But BOT_TOKEN is missing. Check your .env file.")
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
    print(f"Monitoring {len(PRODUCT_CHANNELS)} product channels and {len(COUPON_CHANNELS)} coupon channels.")
    print(f"Tracking {len(PRODUCTS)} products and {len(STORES)} stores.")
    
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
