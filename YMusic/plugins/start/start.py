from pyrogram import filters
from YMusic import app
import config

PREFIX = config.PREFIX
START_COMMAND = ["START", "ST"]
HELP_COMMAND = ["HELP"]

HELP_MESSAGE = f"""
**Commands:**
 `{PREFIX}play|p [nama lagu|audio file]` - Mencari musik dari youtube dan memutarnya (reply audio file)
"""

# @app.on_message(filters.private & filters.command(START_COMMAND, PREFIX))
# async def _start(_, message):
    # await message.reply_text(
        # "Hey user how are you.\nIf you need any help just ping me I am here to help you."
    # )

@app.on_message(filters.command(HELP_COMMAND, PREFIX))
async def _help(_, message):
    await message.reply_text(HELP_MESSAGE)
