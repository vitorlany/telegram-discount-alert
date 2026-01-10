# 🎯 Telegram Discount Alert Bot

This bot monitors specific Telegram channels for product keywords and sends notifications via a dedicated Telegram Bot.

It acts as a bridge between channels you follow and your own notification bot, allowing for automated filtering of deal alerts.

---

## ⚙️ How it works

- **Account Monitoring**: Operates via a Telegram Userbot, observing messages in joined channels.
- **Filtering**: Matches message content against user-defined criteria in `config.yml` using string matching or Regular Expressions (Regex).
- **Notifications**: Forwards matches to a separate Telegram Bot for instant delivery.
- **Session Management**: Supports String Sessions for deployment on environments without persistent storage.

## 🛠️ Setup Guide

### 1. Requirements

- **Telegram Credentials**: `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org).
- **Bot Token**: A token from [@BotFather](https://t.me/botfather).
- **Python 3.8+**: Required for execution.

### 2. Installation

```bash
git clone https://github.com/vitorlany/telegram-discount-alert.git
cd telegram-discount-alert
pip install -r requirements.txt
```

### 3. Configuration

1. **Environment Variables**: Create a `.env` file from `.env.example` and insert your credentials.
2. **Configuration File**: Define channels and products in `config.yml`:
   ```yaml
   channels:
     - "-10012345678" # Use list_channels.py to find IDs
   products:
     - name: "Next-gen GPU"
       regex: "RTX\\s*50[7-9]0"
   ```

### 4. Execution

```bash
python main.py
```

---

## 💡 Utilities

- `list_channels.py`: Displays names and IDs of channels your account is currently in.
- `generate_string_session.py`: Generates a `TG_STRING_SESSION` for cloud deployment.

---

_Developed to automate keyword monitoring in Telegram channels._
