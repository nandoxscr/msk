from YMusic import app
from YMusic.misc import SUDOERS
from YMusic.utils.queue import get_queue
from pyrogram import filters
import time
import config

CURRENT_COMMAND = ["CURRENT", "CR"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

PLAY_START_TIME = {}


def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

@app.on_message((filters.command(CURRENT_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _current(_, message):
    chat_id = message.chat.id

    try:
        queue = get_queue(chat_id)
        if not queue:
            await message.reply_text("Tidak ada lagu dalam antrian.")
            return

        current_song = queue[0]
        title = current_song['title']
        duration = current_song['duration']
        link = current_song['link']

        if chat_id in PLAY_START_TIME:
            elapsed_time = int(time.time() - PLAY_START_TIME[chat_id])
            current_time = format_time(elapsed_time)
            total_duration = format_time(duration)

            await message.reply_text(
                f"🎵 Sedang diputar:\n\n"
                f"Judul: {title}\n"
                f"Durasi: {current_time} / {total_duration}\n"
                f"Link: {link}",
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                f"🎵 Sedang diputar:\n\n"
                f"Judul: {title}\n"
                f"Durasi: {duration}\n"
                f"Link: {link}",
                disable_web_page_preview=True
            )

    except Exception as e:
        await message.reply_text(f"Terjadi kesalahan: {str(e)}")

async def start_play_time(chat_id):
    PLAY_START_TIME[chat_id] = time.time()

async def stop_play_time(chat_id):
    if chat_id in PLAY_START_TIME:
        del PLAY_START_TIME[chat_id]
        