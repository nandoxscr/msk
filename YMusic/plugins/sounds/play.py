from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import searchYt, extract_video_id, download_audio
from YMusic.utils.queue import add_to_queue, get_queue_length, is_queue_empty
from YMusic.misc import SUDOERS

from pyrogram import filters

import asyncio
import random
import time
import config

PLAY_COMMAND = ["P", "PLAY"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX


@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    
    async def process_audio(title, duration, audio_file, link):
        if not is_queue_empty(chat_id):
            queue_num = add_to_queue(chat_id, title[:19], duration, audio_file, link)
            await m.edit(f"# {queue_num}\n{title[:19]}\nSaya telah memasukkan lagu Anda ke dalam antrian.")
        else:
            Status, Text = await userbot.playAudio(chat_id, audio_file)
            if not Status:
                await m.edit(Text)
            else:
                add_to_queue(chat_id, title[:19], duration, audio_file, link)
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Saya sedang memutar lagu Anda sekarang\n\nNama Lagu:- [{title[:19]}]({link})\nDurasi:- {duration}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                    disable_web_page_preview=True,
                )

    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
        m = await message.reply_text("Tunggu...Saya sedang memproses audio Anda....")
        audio_file = await message.reply_to_message.download()
        title = message.reply_to_message.audio.title if message.reply_to_message.audio else "Voice Message"
        duration = message.reply_to_message.audio.duration if message.reply_to_message.audio else 0
        link = message.reply_to_message.link
        await process_audio(title, duration, audio_file, link)
    
    elif len(message.command) < 2:
        await message.reply_text("Siapa yang akan menyebutkan nama lagunya?? 🤔")
    
    else:
        m = await message.reply_text("Tunggu...Saya sedang mencari lagu Anda....")
        query = message.text.split(maxsplit=1)[1]
        try:
            title, duration, link = await searchYt(query)
            if not title:
                return await m.edit("Tidak ada hasil ditemukan")
            
            await m.edit("Tunggu...Saya sedang mengunduh lagu Anda....")
            file_name = f"{title[:50]}"
            audio_file, downloaded_title, audio_duration = await download_audio(link, file_name)
            
            if not audio_file:
                return await m.edit("Gagal mengunduh audio. Silakan coba lagi.")
            
            await process_audio(downloaded_title, audio_duration, audio_file, link)
        
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")
            