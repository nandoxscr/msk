from YMusic import app
from YMusic.core import userbot
from YMusic.utils.ytDetails import searchYt, extract_video_id, download_audio
from YMusic.utils.queue import add_to_queue, get_queue_length, is_queue_empty, get_queue
from YMusic.utils.utils import delete_file
from YMusic.plugins.sounds.current import start_play_time, stop_play_time
from YMusic.misc import SUDOERS

from pyrogram import filters
from collections import defaultdict

import asyncio
import time
import config


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
    
    if ONGOING_PROCESSES[chat_id]:
        await message.reply_text("Proses lain sedang berlangsung. Tunggu sampai selesai.")
        return

    ONGOING_PROCESSES[chat_id] = asyncio.current_task()

    async def process_audio(title, duration, audio_file, link):
        duration_minutes = duration / 60 if isinstance(duration, (int, float)) else 0
        
        if duration_minutes > config.MAX_DURATION_MINUTES:
            await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
            delete_file(audio_file)
            return

        queue_num = add_to_queue(chat_id, title, duration, audio_file, link)
        if queue_num == 1:
            Status, Text = await userbot.playAudio(chat_id, audio_file)
            if not Status:
                await m.edit(Text)
            else:
                finish_time = time.time()
                await start_play_time(chat_id)
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(
                    f"Sedang diputar\n\nJudul: [{title}]({link})\nDurasi: {duration}",
                    disable_web_page_preview=True,
                )
        else:
            await m.edit(f"#{queue_num} - {title}\n\nDitambahkan di daftar putar.")

    try:
        if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
            m = await message.reply_text("Memproses audio....")
            audio_file = await message.reply_to_message.download()
            title = message.reply_to_message.audio.title if message.reply_to_message.audio else "Voice Message"
            duration = message.reply_to_message.audio.duration if message.reply_to_message.audio else 0
            link = message.reply_to_message.link
            
            if duration > config.MAX_DURATION_MINUTES * 60:  # Konversi ke detik
                await m.edit(f"Maaf, audio ini terlalu panjang. Maksimal durasi adalah {config.MAX_DURATION_MINUTES} menit.")
                await delete_file(audio_file) 
                return
            
            await process_audio(title, duration, audio_file, link)
        
        elif len(message.command) < 2:
            await message.reply_text("Mau lagu apa tuan? 🙏")
        
        else:
            m = await message.reply_text("Mencari lagu di youtube....")
            query = message.text.split(maxsplit=1)[1]
            
            title, duration, link = await searchYt(query)
            if not title:
                return await m.edit("Tidak ada hasil ditemukan")
            
            if duration is not None:
                duration_minutes = duration / 60  # Karena duration sekarang dalam detik
                if duration_minutes > MAX_DURATION_MINUTES:
                    await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {MAX_DURATION_MINUTES} menit.")
                    return
            
            await m.edit("Mengunduh audio...")
            file_name = f"{title}"
            audio_file, downloaded_title, audio_duration = await download_audio(link, file_name)
            
            if not audio_file:
                return await m.edit("Gagal mengunduh audio. coba lagi.")
            
            if audio_duration > MAX_DURATION_MINUTES * 60:
                await m.edit(f"Maaf, lagu ini terlalu panjang. Maksimal durasi adalah {MAX_DURATION_MINUTES} menit.")
                await delete_file(audio_file)
                return
            
            await process_audio(downloaded_title, audio_duration, audio_file, link)

    except asyncio.CancelledError:
        await message.reply_text("Proses dibatalkan.")
    except Exception as e:
        await message.reply_text(f"Error:- <code>{e}</code>")
    finally:
        ONGOING_PROCESSES[chat_id] = None        

@app.on_message((filters.command(PLAYLIST_COMMAND, [PREFIX, RPREFIX])) & filters.group)
async def _playlist(_, message):
    chat_id = message.chat.id
    if is_queue_empty(chat_id):
        await message.reply_text("Daftar putar kosong.")
    else:
        queue = get_queue(chat_id)
        playlist = "🎵 **Daftar Putar:**\n\n"
        for i, song in enumerate(queue, start=1):
            duration = song['duration']
            if isinstance(duration, int):
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes:02d}:{seconds:02d}"
            else:
                duration_str = duration

            if i == 1:
                playlist += f"{i}. ▶️ **{song['title']}** - {duration_str}\n"
            else:
                playlist += f"{i}. **{song['title']}** - {duration_str}\n"
            
            if i == 10:
                break
        
        if len(queue) > 10:
            playlist += f"\nDan {len(queue) - 10} lagu lainnya..."
        
        await message.reply_text(playlist)
        
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
