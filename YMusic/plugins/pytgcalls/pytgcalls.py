from pytgcalls import PyTgCalls, filters
from pytgcalls.types import Update, MediaStream

from YMusic import call, app
from YMusic.utils.queue import QUEUE, get_queue, clear_queue, pop_an_item
from YMusic.utils.loop import get_loop, set_loop

import time


async def _skip(chat_id):
    loop = await get_loop(chat_id)
    if loop > 0:
        try:
            chat_queue = get_queue(chat_id)
            if not chat_queue:
                return 1  # Queue is empty
            loop -= 1
            await set_loop(chat_id, loop)
            current_song = chat_queue[0]
            await call.play(
                chat_id,
                MediaStream(
                    current_song['audio_file'],
                    video_flags=MediaStream.Flags.IGNORE,
                ),
            )
            finish_time = time.time()
            return [current_song['title'], current_song['duration'], current_song['link'], finish_time]
        except Exception as e:
            return [2, f"Error:- <code>{e}</code>"]

    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if not chat_queue:
            await stop(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            try:
                pop_an_item(chat_id)  # Remove the current song
                next_song = chat_queue[0]  # Get the next song
                await call.play(
                    chat_id,
                    MediaStream(
                        next_song['audio_file'],
                        video_flags=MediaStream.Flags.IGNORE,
                    ),
                )
                finish_time = time.time()
                return [next_song['title'], next_song['duration'], next_song['link'], finish_time]
            except Exception as e:
                return [2, f"Error:- <code>{e}</code>"]
    await stop(chat_id)
    return 1


@call.on_update(filters.stream_end)
async def handler(client: PyTgCalls, update: Update):
    start_time = time.time()
    chat_id = update.chat_id
    resp = await _skip(chat_id)
    if resp == 1:
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
        await call.leave_call(
            chat_id,
        )
    except:
        pass
