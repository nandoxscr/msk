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
        print("queue empty 1")
        return None

    pop_an_item(chat_id)
    if is_queue_empty(chat_id):
        print("queue empty 2")
        return 1

    next_song = QUEUE[chat_id][0]
    try:
        await call.play(
            chat_id,
            MediaStream(
                next_song['audio_file'],
                video_flags=MediaStream.Flags.IGNORE,
            ),
        )
        return [next_song['title'], next_song['duration'], next_song['link'], time.time()]
    except Exception as e:
        print(f"Error in _skip: {e}")
        return None


@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    chat_id = update.chat_id
    try:
        if is_queue_empty(chat_id):
            await stop(chat_id)
            clear_downloads_cache()
            await stop_play_time(chat_id)
            await app.send_message(chat_id, "Semua lagu telah diputar. Meninggalkan obrolan suara dan membersihkan cache.")
        else:
            result = await _skip(chat_id)
            if isinstance(result, list):
                title, duration, link, _ = result
                await start_play_time(chat_id)
                await app.send_message(
                    chat_id,
                    f"Memutar lagu berikutnya:\n\nJudul: {title}\nDurasi: {duration}\nLink: {link}"
                )
            else:
                await app.send_message(chat_id, "Tidak dapat memutar lagu berikutnya. Meninggalkan obrolan suara.")
                await stop(chat_id)
                await stop_play_time(chat_id)
                clear_downloads_cache()
    except Exception as e:
        print(f"Error in stream_end handler: {e}")
        await app.send_message(chat_id, "Terjadi kesalahan saat mencoba memutar lagu berikutnya. Meninggalkan obrolan suara.")
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