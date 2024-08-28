from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Update, MediaStream

from YMusic import call, app
from YMusic.utils.queue import QUEUE, get_queue, clear_queue, pop_an_item, is_queue_empty, get_current_song
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.formaters import get_readable_time, format_time
from YMusic.utils.utils import clear_downloads_cache, extract_song_title
from YMusic.plugins.sounds.current import start_play_time, stop_play_time
from YMusic.plugins.sounds.music_commands import MAX_MESSAGE_LENGTH, get_lyrics

import time
import asyncio
import logging

logger = logging.getLogger(__name__)

async def _skip(chat_id):
    if is_queue_empty(chat_id):
        print(f"Queue empty for chat {chat_id}")
        return 1

    current_song = pop_an_item(chat_id)
    print(f"Skipped song: {current_song['title']} in chat {chat_id}")

    if is_queue_empty(chat_id):
        print(f"No more songs in queue for chat {chat_id}")
        return 1

    next_song = get_queue(chat_id)[0]
    try:
        print(f"Attempting to play next song: {next_song['title']} in chat {chat_id}")
        await call.play(
            chat_id,
            MediaStream(
                next_song['audio_file'],
                video_flags=MediaStream.Flags.IGNORE,
            ),
        )
        return [next_song['title'], next_song['duration'], next_song['link'], next_song['requester_name'], next_song['requester_id'], time.time()]
    except Exception as e:
        print(f"Error in _skip for chat {chat_id}: {e}")
        return None

@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    chat_id = update.chat_id
    try:
        logger.info(f"Stream ended for chat {chat_id}")

        loop_count = await get_loop(chat_id)
        current_song = get_current_song(chat_id)

        if loop_count > 0 and current_song:
            await set_loop(chat_id, loop_count - 1)
            
            await call.play(
                chat_id,
                MediaStream(
                    current_song['audio_file'],
                    video_flags=MediaStream.Flags.IGNORE,
                ),
            )
            await send_song_info(chat_id, current_song, is_loop=True)
            return

        popped_item = pop_an_item(chat_id)
        if not popped_item:
            logger.info(f"Queue is empty for chat {chat_id}")
            await stop(chat_id)
            clear_downloads_cache()
            await stop_play_time(chat_id)
            await app.send_message(chat_id, "Semua lagu telah diputar. Meninggalkan obrolan suara dan membersihkan cache.")
        else:
            next_song = get_current_song(chat_id)
            if next_song:
                try:
                    logger.info(f"Attempting to play next song: {next_song['title']} in chat {chat_id}")
                    await call.play(
                        chat_id,
                        MediaStream(
                            next_song['audio_file'],
                            video_flags=MediaStream.Flags.IGNORE,
                        ),
                    )
                    await start_play_time(chat_id)
                    await send_song_info(chat_id, next_song)
                except Exception as e:
                    logger.error(f"Error playing next song in chat {chat_id}: {e}")
                    await app.send_message(chat_id, "Terjadi kesalahan saat mencoba memutar lagu berikutnya. Meninggalkan obrolan suara dan membersihkan cache.")
                    await stop(chat_id)
                    await stop_play_time(chat_id)
                    clear_downloads_cache()
            else:
                logger.warning(f"No next song found for chat {chat_id} after popping an item")
                await stop(chat_id)
                await stop_play_time(chat_id)
                clear_downloads_cache()
                await app.send_message(chat_id, "Tidak ada lagu berikutnya. Meninggalkan obrolan suara dan membersihkan cache.")
    except Exception as e:
        logger.error(f"Error in stream_end handler for chat {chat_id}: {e}")
        await app.send_message(chat_id, f"Terjadi kesalahan: {str(e)}. Meninggalkan obrolan suara dan membersihkan cache.")
        await stop(chat_id)
        await stop_play_time(chat_id)
        clear_downloads_cache()

async def send_song_info(chat_id, song, is_loop=False):
    original_query = song.get('query', song['title'])
    processed_query = extract_song_title(original_query)
    title = song['title']
    duration = song['duration']
    link = song['link']
    requester_name = song['requester_name']
    requester_id = song['requester_id']

    lyrics_data = await get_lyrics(processed_query)
    
    message_text = f"🎵 {'Memutar ulang' if is_loop else 'Sedang diputar'}:\n\n"
    
    if lyrics_data:
        message_text += f"Judul: [{title}]({link})\n"
        message_text += f"Artis: {lyrics_data['artist']}\n"
        message_text += f"Durasi: {format_time(duration)}\n"
        message_text += f"Direquest oleh: [{requester_name}](tg://user?id={requester_id})\n\n"
        
        lyrics = lyrics_data['lyrics']
        message_text += f"📜 Lirik:\n{lyrics}"
    else:
        message_text += f"Judul: [{title}]({link})\n"
        message_text += f"Durasi: {format_time(duration)}\n"
        message_text += f"Direquest oleh: [{requester_name}](tg://user?id={requester_id})\n\n"
        message_text += "Lirik tidak ditemukan."

    if len(message_text) > MAX_MESSAGE_LENGTH:
        parts = textwrap.wrap(message_text, MAX_MESSAGE_LENGTH, replace_whitespace=False)
        for part in parts:
            await app.send_message(chat_id, part, disable_web_page_preview=True)
    else:
        await app.send_message(chat_id, message_text, disable_web_page_preview=True)

async def stop(chat_id):
    try:
        if chat_id in QUEUE:
            clear_queue(chat_id)
        await call.leave_call(chat_id)
    except Exception as e:
        logger.error(f"Error in stop: {e}")
    finally:
        clear_downloads_cache()