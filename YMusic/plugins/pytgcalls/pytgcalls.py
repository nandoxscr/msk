from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Update, MediaStream

from YMusic import call, app
from YMusic.core import userbot
from YMusic.utils.queue import QUEUE, get_queue, clear_queue, pop_an_item, is_queue_empty, get_current_song
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.formaters import get_readable_time, format_time
from YMusic.utils.utils import clear_downloads_cache, send_song_info, MAX_MESSAGE_LENGTH
from YMusic.plugins.sounds.current import start_play_time, stop_play_time

import os
import time
import asyncio

@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    chat_id = update.chat_id
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Stream ended for chat {chat_id}")

        loop_count = await get_loop(chat_id)
        current_song = get_current_song(chat_id)
        print(f"Current song before processing: {current_song}")

        if loop_count > 0 and current_song:
            print(f"Looping song: {current_song['title']}, loop count: {loop_count}")
            await set_loop(chat_id, loop_count - 1)
            if current_song['is_video']:
                print("Attempting to play looped video")
                await userbot.playVideo(chat_id, current_song['audio_file'])
            else:
                print("Attempting to play looped audio")
                await userbot.playAudio(chat_id, current_song['audio_file'])
            await send_song_info(chat_id, current_song, is_loop=True)
            return

        print("Popping item from queue")
        popped_item = pop_an_item(chat_id)
        print(f"Popped item: {popped_item}")

        if not popped_item:
            print(f"Queue is empty for chat {chat_id}")
            await stop(chat_id)
            await clear_downloads_cache()
            await stop_play_time(chat_id)
            await app.send_message(chat_id, "Semua lagu telah diputar. Meninggalkan obrolan suara dan membersihkan cache.")
        else:
            next_song = get_current_song(chat_id)
            print(f"Next song: {next_song}")
            if next_song:
                try:
                    print(f"Attempting to play next song: {next_song['title']} in chat {chat_id}, is_video: {next_song['is_video']}")
                    
                    # Check if the file exists
                    if os.path.exists(next_song['audio_file']):
                        if next_song['is_video']:
                            print("Playing video")
                            await userbot.playVideo(chat_id, next_song['audio_file'])
                        else:
                            print("Playing audio")
                            await userbot.playAudio(chat_id, next_song['audio_file'])
                        
                        print("Starting play time")
                        await start_play_time(chat_id)
                        print("Sending song info")
                        await send_song_info(chat_id, next_song)
                    else:
                        print(f"File not found: {next_song['audio_file']}")
                        raise FileNotFoundError(f"File not found: {next_song['audio_file']}")
                    
                except Exception as e:
                    print(f"Error playing next song in chat {chat_id}: {e}")
                    await app.send_message(chat_id, f"Terjadi kesalahan saat mencoba memutar lagu berikutnya: {str(e)}. Meninggalkan obrolan suara dan membersihkan cache.")
                    await stop(chat_id)
                    await stop_play_time(chat_id)
                    await clear_downloads_cache()
            else:
                print(f"No next song found for chat {chat_id} after popping an item")
                await stop(chat_id)
                await stop_play_time(chat_id)
                await clear_downloads_cache()
                await app.send_message(chat_id, "Tidak ada lagu berikutnya. Meninggalkan obrolan suara dan membersihkan cache.")
    except Exception as e:
        print(f"Error in stream_end handler for chat {chat_id}: {e}")
        await app.send_message(chat_id, f"Terjadi kesalahan: {str(e)}. Meninggalkan obrolan suara dan membersihkan cache.")
        await stop(chat_id)
        await stop_play_time(chat_id)
        await clear_downloads_cache()

async def stop(chat_id):
    try:
        if chat_id in QUEUE:
            clear_queue(chat_id)
        await call.leave_call(chat_id)
    except Exception as e:
        print(f"Error in stop: {e}")
    finally:
        await clear_downloads_cache()