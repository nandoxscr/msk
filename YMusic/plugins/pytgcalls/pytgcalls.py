from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Update, MediaStream

from YMusic import call, app
from YMusic.utils.queue import QUEUE, get_queue, clear_queue, pop_an_item, is_queue_empty
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.utils import clear_downloads_cache
from YMusic.plugins.sounds.current import start_play_time, stop_play_time

import time


async def _skip(chat_id):
    if is_queue_empty(chat_id):
        print(f"Queue empty for chat {chat_id}")
        return None

    current_song = get_current_song(chat_id)
    if not current_song:
        print(f"No current song for chat {chat_id}")
        return None

    next_song = pop_an_item(chat_id)
    if not next_song:
        print(f"Failed to get next song for chat {chat_id}")
        return None

    try:
        print(f"Attempting to play next song: {next_song['title']} in chat {chat_id}")
        await call.play(
            chat_id,
            MediaStream(
                next_song['audio_file'],
                video_flags=MediaStream.Flags.IGNORE,
            ),
        )
        return [next_song['title'], next_song['duration'], next_song['link'], time.time()]
    except Exception as e:
        print(f"Error in _skip for chat {chat_id}: {e}")
        return None

@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    chat_id = update.chat_id
    try:
        print(f"Stream ended for chat {chat_id}")
        if is_queue_empty(chat_id):
            print(f"Queue is empty for chat {chat_id}")
            await stop(chat_id)
            clear_downloads_cache()
            await stop_play_time(chat_id)
            await app.send_message(chat_id, "Semua lagu telah diputar. Meninggalkan obrolan suara dan membersihkan cache.")
        else:
            current_song = get_current_song(chat_id)  # Tambahkan fungsi ini di queue.py
            if current_song:
                print(f"Current song for chat {chat_id}: {current_song['title']}")
                result = await _skip(chat_id)
                if result:
                    title, duration, link, _ = result
                    await start_play_time(chat_id)
                    await app.send_message(
                        chat_id,
                        f"Memutar lagu berikutnya:\n\nJudul: {title}\nDurasi: {duration}\nLink: {link}",
                        disable_web_page_preview=True
                    )
                else:
                    print(f"Failed to play next song for chat {chat_id}")
                    await app.send_message(chat_id, "Tidak dapat memutar lagu berikutnya. Meninggalkan obrolan suara dan membersihkan cache.")
                    await stop(chat_id)
                    await stop_play_time(chat_id)
                    clear_downloads_cache()
            else:
                print(f"No current song for chat {chat_id}, but queue is not empty")
                # Handle this case, maybe try to play the next song
    except Exception as e:
        print(f"Error in stream_end handler for chat {chat_id}: {e}")
        await app.send_message(chat_id, f"Terjadi kesalahan saat mencoba memutar lagu berikutnya: {str(e)}. Meninggalkan obrolan suara dan membersihkan cache.")
        await stop(chat_id)
        await stop_play_time(chat_id)
        clear_downloads_cache()

async def stop(chat_id):
    try:
        if chat_id in QUEUE:
            QUEUE.pop(chat_id)
        await call.leave_call(chat_id)
    except Exception as e:
        print(f"Error in stop: {e}")
    finally:
        clear_downloads_cache()