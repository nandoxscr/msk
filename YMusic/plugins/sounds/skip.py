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

@app.on_message((filters.command(SKIP_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aSkip(_, message):
    start_time = time.time()
    chat_id = message.chat.id

    # Get administrators
    administrators = []
    async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        administrators.append(m)

    if (message.from_user.id in SUDOERS) or (message.from_user.id in [admin.user.id for admin in administrators]):
        m = await message.reply_text("Mencoba melewati lagu saat ini...")
        loop = await get_loop(chat_id)
        if loop != 0:
            return await m.edit_text(f"Loop diaktifkan untuk lagu saat ini. Harap nonaktifkan dengan {PREFIX}endloop untuk melewati lagu.")
        
        if is_queue_empty(chat_id):
            await stop(chat_id)
            await m.edit_text("Antrian kosong. Saya meninggalkan obrolan suara...")
            return

        try:
            pop_an_item(chat_id)  # Remove current song
            if is_queue_empty(chat_id):
                await stop(chat_id)
                await m.edit_text("Tidak ada lagu berikutnya. Saya meninggalkan obrolan suara...")
                return

            next_song = get_queue(chat_id)[0]
            title, duration, songlink, link = next_song[1], next_song[2], next_song[3], next_song[4]
            
            await call.play(
                chat_id,
                MediaStream(
                    songlink,
                    video_flags=MediaStream.Flags.AUTO_DETECT,
                ),
            )
            finish_time = time.time()
            total_time_taken = str(int(finish_time - start_time)) + "s"
            await m.edit_text(
                f"Memutar lagu Anda\n\nNama Lagu:- [{title}]({link})\nDurasi:- {duration}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                disable_web_page_preview=True,
            )
        except Exception as e:
            await m.edit_text(f"Error:- <code>{e}</code>")
    else:
        await message.reply_text("Maaf, hanya admin dan SUDOERS yang dapat melewati lagu.")

@app.on_message(filters.command("queue", [PREFIX, RPREFIX]) & filters.group)
async def _queue(_, message):
    chat_id = message.chat.id
    if not is_queue_empty(chat_id):
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await message.reply_text("Antrian kosong")
            return
        queue = chat_queue[1:]
        output = "**Antrian:**\n"
        for i, item in enumerate(queue):
            title, duration, link = item[1], item[2], item[4]
            output += f"{i + 1}. [{title}]({link}) - {duration}\n"
        await message.reply_text(output, disable_web_page_preview=True)
    else:
        await message.reply_text("Antrian kosong")

async def stop(chat_id):
    try:
        await call.leave_call(chat_id)
    except:
        pass