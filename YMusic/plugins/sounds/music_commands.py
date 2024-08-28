from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import searchYt, extract_video_id, download_audio
from YMusic.utils.queue import add_to_queue, get_queue_length, is_queue_empty, get_queue, MAX_QUEUE_SIZE, get_current_song
from YMusic.utils.utils import delete_file, extract_song_title
from YMusic.utils.formaters import get_readable_time, format_time
from YMusic.plugins.sounds.current import start_play_time, stop_play_time
from YMusic.misc import SUDOERS

from pyrogram import filters
from collections import defaultdict

import asyncio
import time
import config
import aiohttp
import json
from urllib.parse import quote
import textwrap

MAX_MESSAGE_LENGTH = 4096

PLAY_COMMAND = ["P", "PLAY"]
PLAYLIST_COMMAND = ["PLAYLIST", "PL"]
CANCEL_COMMAND = ["CANCEL"]
PREFIX = config.PREFIX
RPREFIX = config.RPREFIX
ONGOING_PROCESSES = defaultdict(lambda: None)

@app.on_message((filters.command(PLAY_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _aPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    requester_name = message.from_user.first_name
    requester_id = message.from_user.id

    if ONGOING_PROCESSES[chat_id]:
        await message.reply_text("Proses lain sedang berlangsung. Tunggu sampai selesai.")
        return

    ONGOING_PROCESSES[chat_id] = asyncio.current_task()

    async def process_audio(title, duration, audio_file, link, original_query):
        duration_minutes = duration / 60 if isinstance(duration, (int, float)) else 0

        if duration_minutes > config.MAX_DURATION_MINUTES:
            await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
            await delete_file(audio_file)
            return

        queue_length = get_queue_length(chat_id)
        if queue_length >= MAX_QUEUE_SIZE:
            await m.edit(f"Maaf, antrian sudah penuh (maksimal {MAX_QUEUE_SIZE} lagu). Tunggu sampai beberapa lagu selesai diputar.")
            await delete_file(audio_file)
            return

        processed_query = extract_song_title(original_query)
        queue_num = add_to_queue(chat_id, title, duration, audio_file, link, requester_name, requester_id, processed_query)
        if queue_num == 1:
            Status, Text = await userbot.playAudio(chat_id, audio_file)
            if not Status:
                await m.edit(Text)
            else:
                finish_time = time.time()
                await start_play_time(chat_id)
                total_time_taken = str(int(finish_time - start_time)) + "s"
                duration_str = format_time(duration)
                
                lyrics_data = await get_lyrics(processed_query)
                
                if lyrics_data:
                    message_text = (
                        f"🎵 Sedang diputar:\n\n"
                        f"Judul: [{title}]({link})\n"
                        f"Artis: {lyrics_data['artist']}\n"
                        f"Durasi: {duration_str}\n"
                        f"Direquest oleh: [{requester_name}](tg://user?id={requester_id})\n\n"
                        f"📜 Lirik:\n{lyrics_data['lyrics'][:1000]}..."  # Batasi lirik ke 1000 karakter
                    )
                else:
                    message_text = (
                        f"🎵 Sedang diputar:\n\n"
                        f"Judul: [{title}]({link})\n"
                        f"Durasi: {duration_str}\n"
                        f"Direquest oleh: [{requester_name}](tg://user?id={requester_id})\n\n"
                        f"Lirik tidak ditemukan."
                    )
                
                await m.edit(message_text, disable_web_page_preview=True)
        elif queue_num:
            await m.edit(f"#{queue_num} - {title}\n\nDitambahkan di daftar putar oleh [{requester_name}](tg://user?id={requester_id}).")
        else:
            await m.edit(f"Gagal menambahkan lagu ke antrian. Antrian mungkin sudah penuh.")

    try:
        if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
            m = await message.reply_text("Memproses audio....")
            audio_file = await message.reply_to_message.download()
            title = message.reply_to_message.audio.title if message.reply_to_message.audio else "Voice Message"
            duration = message.reply_to_message.audio.duration if message.reply_to_message.audio else 0
            link = message.reply_to_message.link
            original_query = title

            if duration > config.MAX_DURATION_MINUTES * 60:
                await m.edit(f"Maaf, audio ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
                await delete_file(audio_file) 
                return

            await process_audio(title, duration, audio_file, link, original_query)

        elif len(message.command) < 2:
            await message.reply_text("Mau lagu apa tuan? 🙏")

        else:
            m = await message.reply_text("Mencari lagu di youtube....")
            original_query = message.text.split(maxsplit=1)[1]

            title, duration, link = await searchYt(original_query)
            if not title:
                return await m.edit("Tidak ada hasil ditemukan")

            if duration is not None:
                duration_minutes = duration / 60
                if duration_minutes > config.MAX_DURATION_MINUTES:
                    await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
                    return

            await m.edit("Mengunduh audio...")
            file_name = f"{title}"
            audio_file, downloaded_title, audio_duration = await download_audio(link, file_name)

            if not audio_file:
                return await m.edit("Gagal mengunduh audio. coba lagi.")

            if audio_duration > config.MAX_DURATION_MINUTES * 60:
                await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
                await delete_file(audio_file)
                return

            await process_audio(downloaded_title, audio_duration, audio_file, link, original_query)

    except asyncio.CancelledError:
        await message.reply_text("Proses dibatalkan.")
    except Exception as e:
        await message.reply_text(f"<code>Error: {e}</code>")
    finally:
        ONGOING_PROCESSES[chat_id] = None  

@app.on_message((filters.command(PLAYLIST_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _playlist(_, message):
    chat_id = message.chat.id
    if is_queue_empty(chat_id):
        await message.reply_text("Daftar putar kosong.")
    else:
        queue = get_queue(chat_id)
        playlist = "🎵 <b>Daftar Putar:</b>\n\n"
        for i, song in enumerate(queue, start=1):
            duration = song['duration']
            duration_str = format_time(duration)

            if i == 1:
                playlist += f"{i}. ▶️ {song['title']} - {duration_str}\n"
                playlist += f"   Direquest oleh: [{song['requester_name']}](tg://user?id={song['requester_id']})\n\n"
            else:
                playlist += f"{i}. {song['title']} - {duration_str}\n"
                playlist += f"   Direquest oleh: [{song['requester_name']}](tg://user?id={song['requester_id']})\n\n"
            
            if i == MAX_QUEUE_SIZE:
                break
        
        if len(queue) > MAX_QUEUE_SIZE:
            playlist += f"\nDan {len(queue) - MAX_QUEUE_SIZE} lagu lainnya..."
        
        await message.reply_text(playlist, disable_web_page_preview=True)


@app.on_message((filters.command(CANCEL_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _cancel(_, message):
    chat_id = message.chat.id
    
    if not ONGOING_PROCESSES[chat_id]:
        await message.reply_text("Tidak ada proses yang sedang berlangsung untuk dibatalkan.")
        return

    task = ONGOING_PROCESSES[chat_id]
    if isinstance(task, asyncio.Task) and not task.done():
        task.cancel()
        await message.reply_text("Proses dibatalkan.")
    else:
        await message.reply_text("Tidak dapat membatalkan proses saat ini.")
    
    ONGOING_PROCESSES[chat_id] = None


async def get_lyrics(query):
    encoded_query = quote(query)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.safone.dev/lyrics?title={encoded_query}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return None