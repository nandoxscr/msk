from YMusic import app
from YMusic.utils.queue import QUEUE, pop_an_item, get_queue, clear_queue, is_queue_empty
from YMusic.utils.loop import get_loop
from YMusic.misc import SUDOERS
from YMusic.plugins.pytgcalls.pytgcalls import _skip
from YMusic.plugins.sounds.current import start_play_time, stop_play_time

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

    # Dapatkan daftar administrator
    administrators = []
    async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(admin)

    if (message.from_user.id in SUDOERS) or (message.from_user.id in [admin.user.id for admin in administrators]):
        # Periksa apakah ada lagu yang sedang diputar
        if is_queue_empty(chat_id):
            await message.reply_text("Tidak ada lagu yang sedang diputar untuk di-skip.")
            return

        m = await message.reply_text("Mencoba melewati lagu saat ini...")
        await stop_play_time(chat_id)
        try:
            result = await _skip(chat_id)
            
            if isinstance(result, int):
                if result == 1:
                    await m.edit("Antrian kosong. Meninggalkan obrolan suara...")
                else:
                    await m.edit("Terjadi kesalahan saat melewati lagu.")
            elif isinstance(result, list):
                title, duration, link, _ = result
                await start_play_time(chat_id)
                await m.edit(
                    f"Berhasil melewati lagu. Sekarang memutar:\n\n"
                    f"Judul: {title}\n"
                    f"Durasi: {duration}\n"
                    f"Link: {link}",
                    disable_web_page_preview=True  # Menonaktifkan preview web
                )
            else:
                await m.edit("Terjadi kesalahan yang tidak terduga saat melewati lagu.")
        
        except IndexError:
            await m.edit("Lagu berhasil dilewati, tetapi terjadi kesalahan saat mengambil informasi lagu berikutnya.")
        except Exception as e:
            await m.edit(f"Terjadi kesalahan: {str(e)}")
    else:
        await message.reply_text("Maaf, hanya admin dan SUDOERS yang dapat melewati lagu.")
        