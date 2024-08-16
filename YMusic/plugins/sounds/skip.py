import logging
from YMusic import app, call
from YMusic.utils.queue import QUEUE, pop_an_item, get_queue, clear_queue, is_queue_empty
from YMusic.utils.loop import get_loop
from YMusic.misc import SUDOERS

from pytgcalls.types import MediaStream
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter

import time
import config

SKIP_COMMAND = ["SKIP"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.on_message((filters.command(SKIP_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aSkip(_, message):
    start_time = time.time()
    chat_id = message.chat.id

    logger.debug(f"Skip command received for chat_id: {chat_id}")

    # Get administrators
    administrators = []
    async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(m)

    if (message.from_user.id in SUDOERS) or (message.from_user.id in [admin.user.id for admin in administrators]):
        m = await message.reply_text("Mencoba melewati lagu saat ini...")
        
        try:
            loop = await get_loop(chat_id)
            if loop != 0:
                return await m.edit_text(f"Loop diaktifkan untuk lagu saat ini. Harap nonaktifkan dengan {PREFIX}endloop untuk melewati lagu.")
            
            logger.debug(f"Current queue state for chat_id {chat_id}: {QUEUE.get(chat_id, [])}")
            
            if is_queue_empty(chat_id):
                logger.debug(f"Queue is empty for chat_id {chat_id}")
                await stop(chat_id)
                await m.edit_text("Antrian kosong. Saya meninggalkan obrolan suara...")
                return

            current_song = pop_an_item(chat_id)
            logger.debug(f"Popped item from queue: {current_song}")

            if is_queue_empty(chat_id):
                logger.debug(f"Queue became empty after popping for chat_id {chat_id}")
                await stop(chat_id)
                await m.edit_text("Tidak ada lagu berikutnya. Saya meninggalkan obrolan suara...")
                return

            next_song = get_queue(chat_id)[0]
            logger.debug(f"Next song to play: {next_song}")

            title, duration, songlink, link = next_song[1], next_song[2], next_song[3], next_song[4]
            
            try:
                await call.play(
                    chat_id,
                    MediaStream(
                        songlink,
                        video_flags=MediaStream.Flags.AUTO_DETECT,
                    ),
                )
            except Exception as e:
                logger.error(f"Error playing next song: {e}")
                await m.edit_text(f"Error memutar lagu berikutnya: {e}")
                return

            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit_text(
                f"Memutar lagu Anda\n\nNama Lagu:- [{title}]({link})\nDurasi:- {duration}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Unexpected error in _aSkip: {e}")
            await m.edit_text(f"Terjadi kesalahan yang tidak terduga: {e}")
    else:
        await message.reply_text("Maaf, hanya admin dan SUDOERS yang dapat melewati lagu.")

async def stop(chat_id):
    try:
        await call.leave_call(chat_id)
    except Exception as e:
        logger.error(f"Error leaving call for chat_id {chat_id}: {e}")