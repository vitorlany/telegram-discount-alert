import os
import asyncio
import questionary
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = os.getenv('TG_SESSION_NAME', 'discount_bot')

# Initialize the client
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

async def main():
    print("Fetching your channels and groups...")
    dialogs = []
    
    # Iterate over all dialogs (chats)
    async for dialog in client.iter_dialogs():
        # Filter for Channels and Groups
        if dialog.is_channel or dialog.is_group:
            dialogs.append(dialog)
    
    if not dialogs:
        print("No channels or groups found.")
        return

    # Create choices for questionary
    choices = [
        questionary.Choice(
            title=f"{dialog.name} (ID: {dialog.id})",
            value=dialog
        )
        for dialog in dialogs
    ]

    # Interactive selection
    selected_dialogs = await questionary.checkbox(
        "Select the channels/groups you want to LEAVE (use space to select, enter to confirm):",
        choices=choices,
        style=questionary.Style([
            ('qmark', 'fg:#673ab7 bold'),       # Question mark
            ('question', 'bold'),               # Question text
            ('answer', 'fg:#f44336 bold'),      # Submitted answer
            ('pointer', 'fg:#673ab7 bold'),     # Selection pointer
            ('highlighted', 'fg:#673ab7 bold'), # Highlighted item
            ('selected', 'fg:#cc5454'),         # Selected item
            ('separator', 'fg:#cc5454'),        # Separator
            ('instruction', ''),                # User instructions
        ])
    ).ask_async()

    if not selected_dialogs:
        print("No channels selected. Exiting.")
        return

    # Confirmation
    print("\n" + "!" * 40)
    print(f"WARNING: You are about to leave {len(selected_dialogs)} channel(s)/group(s):")
    for d in selected_dialogs:
        print(f" - {d.name}")
    print("!" * 40)
    
    confirm = await questionary.confirm("Are you sure you want to proceed?").ask_async()
    
    if confirm:
        print("\nProcessing leave requests...")
        for d in selected_dialogs:
            try:
                # delete_dialog leaves the group/channel
                await client.delete_dialog(d.id)
                print(f"[SUCCESS] Left: {d.name}")
                # Add a small delay to avoid hitting rate limits too fast
                await asyncio.sleep(1) 
            except Exception as e:
                print(f"[ERROR] Failed to leave {d.name} (ID: {d.id}): {e}")
        print("\nDone.")
    else:
        print("Operation cancelled. No changes were made.")

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
