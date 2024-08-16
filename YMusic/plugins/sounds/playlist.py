from YMusic import app
from YMusic.utils.queue import get_queue, is_queue_empty
from pyrogram import filters
import config

PLAYLIST_COMMAND = ["PLAYLIST", "QUEUE"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

@app.on_message((filters.command(PLAYLIST_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _playlist(_, message):
    chat_id = message.chat.id
    if is_queue_empty(chat_id):
        await message.reply_text("Antrian lagu kosong.")
        return

    queue = get_queue(chat_id)
    playlist = "🎵 **Daftar Antrian Lagu:**\n\n"
    for i, song in enumerate(queue, start=1):
        playlist += f"{i}. **{song['title']}** - {song['duration']}\n"
        if i == 1:
            playlist += "   ▶️ Sedang diputar\n"
        if i == 10:
            break  # Batasi hanya 10 lagu yang ditampilkan

    if len(queue) > 10:
        playlist += f"\nDan {len(queue) - 10} lagu lainnya..."

    await message.reply_text(playlist)