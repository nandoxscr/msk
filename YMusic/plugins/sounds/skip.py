from YMusic import app
from YMusic.utils.queue import QUEUE, pop_an_item, get_queue, clear_queue, is_queue_empty
from YMusic.utils.loop import get_loop
from YMusic.misc import SUDOERS
from YMusic.plugins.pytgcalls.pytgcalls import _skip, stop
from YMusic.plugins.sounds.current import start_play_time, stop_play_time
from YMusic.utils.utils import clear_downloads_cache
from YMusic.utils.formaters import get_readable_time, format_time

from pytgcalls.types import MediaStream
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter

import time
import config
import logging

SKIP_COMMAND = ["SKIP"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

@app.on_message((filters.command(SKIP_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aSkip(_, message):
    chat_id = message.chat.id
    administrators = []
    async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(admin)

    if (message.from_user.id in SUDOERS) or (message.from_user.id in [admin.user.id for admin in administrators]):
        if is_queue_empty(chat_id):
            await message.reply_text("Tidak ada lagu yang sedang diputar untuk di-skip.")
            return

        m = await message.reply_text("Mencoba melewati lagu saat ini...")
        await stop_play_time(chat_id)
        try:
            result = await _skip(chat_id)
            if result == 1:
                await m.edit("Tidak ada lagu berikutnya. Meninggalkan obrolan suara...")
                await stop(chat_id)
                clear_downloads_cache()
            elif isinstance(result, list):
                title, duration, link, _ = result
                await start_play_time(chat_id)
                duration_str = format_time(duration)
                await m.edit(
                    f"Berhasil melewati lagu. Sedang diputar:\n\n"
                    f"Judul: [{title}]({link})\n"
                    f"Durasi: {duration_str}\n",
                    disable_web_page_preview=True
                )
            else:
                await m.edit("Tidak ada lagu berikutnya. Meninggalkan obrolan suara...")
                await stop(chat_id)
                clear_downloads_cache()
        
        except Exception as e:
            await m.edit(f"Terjadi kesalahan: {str(e)}")
    else:
        await message.reply_text("Maaf, hanya admin dan user yang diizinkan yang dapat melewati lagu.")
