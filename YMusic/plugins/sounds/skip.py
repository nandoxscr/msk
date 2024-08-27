from YMusic import app
from YMusic.utils.queue import QUEUE, pop_an_item, get_queue, clear_queue, is_queue_empty
from YMusic.utils.loop import get_loop
from YMusic.misc import SUDOERS
from YMusic.plugins.pytgcalls.pytgcalls import _skip, stop, send_song_info
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

logger = logging.getLogger(__name__)

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
            popped_item = pop_an_item(chat_id)
            if not popped_item:
                await m.edit("Tidak ada lagu berikutnya. Meninggalkan obrolan suara...")
                await stop(chat_id)
                clear_downloads_cache()
            else:
                next_song = get_current_song(chat_id)
                if next_song:
                    await call.play(
                        chat_id,
                        MediaStream(
                            next_song['audio_file'],
                            video_flags=MediaStream.Flags.IGNORE,
                        ),
                    )
                    await start_play_time(chat_id)
                    await m.delete()
                    await send_song_info(chat_id, next_song)
                else:
                    await m.edit("Tidak ada lagu berikutnya. Meninggalkan obrolan suara...")
                    await stop(chat_id)
                    clear_downloads_cache()
        except Exception as e:
            logger.error(f"Error in _aSkip for chat {chat_id}: {e}")
            await m.edit(f"Terjadi kesalahan: {str(e)}")
    else:
        await message.reply_text("Maaf, hanya admin dan user yang diizinkan yang dapat melewati lagu.")
        