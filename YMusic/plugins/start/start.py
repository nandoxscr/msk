from pyrogram import filters
from YMusic import app
import config

PREFIX = config.PREFIX
START_COMMAND = ["START", "ST"]
HELP_COMMAND = ["HELP"]

HELP_MESSAGE = f"""
🙇 = Semua orang
🧑‍🔧 = Admin saja
**Commands:**
🙇| `{PREFIX}play [nama lagu|audio file]` - <i>Mencari musik dari youtube dan memutarnya (reply audio file)</i>
🧑‍🔧| `{PREFIX}pause` - <i>Pause musik</i>
🧑‍🔧| `{PREFIX}resume` - <i>Resume musik</i>
🧑‍🔧| `{PREFIX}stop` - <i>Mengakhiri musik</i>
🧑‍🔧| `{PREFIX}skip` - <i>Melewati lagu sekarang dan melanjutkan ke lagu berikutnya</i>
🧑‍🔧| `{PREFIX}loop` - <i>Memutar ulang lagu yang sedang diputar sebanyak 5x</i>
🧑‍🔧| `{PREFIX}endloop` - <i>Mematikan pemutaran ulang</i>

**Extra**
🙇| `{PREFIX}lyric [nama lagu]` - <i>Mencari lirik lagu</i>
🙇| `{PREFIX}nando [query]` - <i>Ini adalah AI, kamu bisa menanyakan apa saja, saya akan menjawab sebaik-baiknya</i>
"""

# @app.on_message(filters.private & filters.command(START_COMMAND, PREFIX))
# async def _start(_, message):
    # await message.reply_text(
        # "Hey user how are you.\nIf you need any help just ping me I am here to help you."
    # )

@app.on_message(filters.command(HELP_COMMAND, PREFIX))
async def _help(_, message):
    await message.reply_text(HELP_MESSAGE)
