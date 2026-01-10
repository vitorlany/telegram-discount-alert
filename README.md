# 🎯 Telegram Discount Alert Bot

A powerful, lightweight Telegram Userbot that monitors your channels for specific products and alerts you instantly via a dedicated Telegram Bot for push notifications.

## ✨ Features

- **Real-time Monitoring**: Running on your own account, it sees everything you see.
- **Regex Support**: Use powerful Regular Expressions to match exactly the deals you want.
- **Push Notifications**: Uses the Telegram Bot API to send loud alerts to your phone (avoiding the silent "Saved Messages" limitation).
- **Cloud Ready**: Supports String Sessions for easy deployment on Oracle Cloud, Railway, or VPS.
- **Customizable**: Easy-to-edit `config.yml` for channels, products, and alert templates.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Telegram API Credentials (`api_id` and `api_hash`) from [my.telegram.org](https://my.telegram.org).
- A Bot Token from [@BotFather](https://t.me/botfather).

### 2. Installation

```bash
git clone https://github.com/vitorlany/telegram-discount-alert.git
cd telegram-discount-alert
pip install -r requirements.txt
```

### 3. Configuration

1. Rename `.env.example` to `.env`.
2. Fill in your `TG_API_ID`, `TG_API_HASH`, and `BOT_TOKEN`.
3. Open `config.yml` to add your channels and product regex:
   ```yaml
   channels:
     - "-10012345678" # Use list_channels.py to find IDs
   products:
     - name: "GPU"
       regex: "RTX\\s*50[7-9]0"
   ```

### 4. Run it

```bash
python main.py
```

## 🛠️ Utility Scripts

- **`list_channels.py`**: Run this to see names and IDs of all channels you are in.
- **`generate_string_session.py`**: Generates a `TG_STRING_SESSION` for cloud deployment (no more `.session` files needed!).
