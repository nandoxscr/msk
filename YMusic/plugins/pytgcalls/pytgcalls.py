from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Update, MediaStream

from YMusic import call, app
from YMusic.utils.queue import QUEUE, get_queue, clear_queue, pop_an_item
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.utils import clear_downloads_cache

import time


async def _skip(chat_id):
    try:
        if chat_id not in QUEUE or not QUEUE[chat_id]:
            return 1  # Antrian kosong

        pop_an_item(chat_id)
        if not QUEUE[chat_id]:
            await stop(chat_id)
            return 1  # Antrian kosong setelah skip

        next_song = QUEUE[chat_id][0]
        await call.play(
            chat_id,
            MediaStream(
                next_song['audio_file'],
                video_flags=MediaStream.Flags.IGNORE,
            ),
        )
        return [next_song['title'], next_song['duration'], next_song['link'], time.time()]
    except IndexError:
        # Jika terjadi IndexError, kemungkinan antrian sudah kosong
        await stop(chat_id)
        return 1
    except Exception as e:
        print(f"Error in _skip: {e}")
        return 2  # Kode error umum


@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    start_time = time.time()
    chat_id = update.chat_id
    resp = await _skip(chat_id)
    if resp == 1:
        clear_downloads_cache()
        await app.send_message(chat_id, "Antrian kosong. Meninggalkan obrolan suara.")
    elif isinstance(resp, list) and resp[0] == 2:
        await app.send_message(chat_id, resp[1])
    elif isinstance(resp, list) and len(resp) == 4:
        total_time_taken = str(int(time.time() - start_time)) + "s"
        await app.send_message(
            chat_id,
            f"Memutar lagu Anda\n\nNama Lagu:- [{resp[0]}]({resp[2]})\nDurasi:- {resp[1]}\nWaktu yang dibutuhkan untuk memutar:- {total_time_taken}",
            disable_web_page_preview=True,
        )
    else:
        await app.send_message(chat_id, "Terjadi kesalahan yang tidak terduga.")


async def stop(chat_id):
    try:
        await call.leave_call(chat_id)
    except:
        pass
    finally:
        clear_downloads_cache()
        