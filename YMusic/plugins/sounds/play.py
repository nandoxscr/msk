from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import searchYt, extract_video_id, download_audio
from YMusic.utils.queue import QUEUE, add_to_queue
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
    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
        m = await message.reply_text("Tunggu...Saya sedang mengunduh audio Anda....")
        audio_file = await message.reply_to_message.download()
        await m.edit("Tunggu...Saya ingin memutar audio Anda...")
        Status, Text = await userbot.playAudio(chat_id, audio_file)
        if not Status:
            await m.edit(Text)
        else:
            if chat_id in QUEUE:
                queue_num = add_to_queue(
                    chat_id,
                    message.reply_to_message.audio.title[:19] if message.reply_to_message.audio else "Voice Message",
                    message.reply_to_message.audio.duration if message.reply_to_message.audio else 0,
                    audio_file,
                    message.reply_to_message.link,
                )
                await m.edit(f"# {queue_num}\nSaya telah memasukkan audio Anda ke dalam antrian.")
            else:
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Saya sedang memutar audio Anda sekarang\n\nNama Audio:- {message.reply_to_message.audio.title[:19] if message.reply_to_message.audio else 'Voice Message'}\nDurasi:- {message.reply_to_message.audio.duration if message.reply_to_message.audio else 'N/A'}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                    disable_web_page_preview=True,
                )
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
            
            if chat_id in QUEUE:
                queue_num = add_to_queue(chat_id, downloaded_title[:19], audio_duration, audio_file, link)
                await m.edit(f"# {queue_num}\n{downloaded_title[:19]}\nSaya telah memasukkan lagu Anda ke dalam antrian.")
            else:
                Status, Text = await userbot.playAudio(chat_id, audio_file)
                if not Status:
                    await m.edit(Text)
                else:
                    add_to_queue(chat_id, downloaded_title[:19], audio_duration, audio_file, link)
                    finish_time = time.time()
                    total_time_taken = str(int(finish_time - start_time)) + "s"
                    await m.edit(
                        f"Saya sedang memutar lagu Anda sekarang\n\nNama Lagu:- [{downloaded_title[:19]}]({link})\nDurasi:- {audio_duration}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                        disable_web_page_preview=True,
                    )
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")


@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if (message.reply_to_message) is not None:
        await message.reply_text("Saat ini fitur ini belum didukung")
    elif (len(message.command)) < 3:
        await message.reply_text("Anda Lupa Memberikan Argumen")
    else:
        m = await message.reply_text("Mencari Query Anda...")
        query = message.text.split(" ", 2)[2]
        msg_id = message.text.split(" ", 2)[1]
        try:
            title, duration, link = await searchYt(query)
            if not title:
                return await m.edit("Tidak ada hasil ditemukan")
            
            await m.edit("Mengunduh...")
            file_name = f"{title[:50]}"
            audio_file, downloaded_title, audio_duration = await download_audio(link, file_name)
            
            if not audio_file:
                return await m.edit("Gagal mengunduh audio. Silakan coba lagi.")
            
            Status, Text = await userbot.playAudio(msg_id, audio_file)
            if Status == False:
                await m.edit(Text)
            else:
                if audio_duration is None:
                    audio_duration = "Memutar Dari LiveStream"
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Saya sedang memutar lagu Anda sekarang\n\nNama Lagu:- [{downloaded_title[:19]}]({link})\nDurasi:- {audio_duration}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
                    disable_web_page_preview=True,
                )
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")