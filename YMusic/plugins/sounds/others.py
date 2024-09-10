from pyrogram import filters
from pyrogram.enums import ChatMembersFilter

from YMusic import app
from YMusic.utils.queue import clear_queue
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.utils import clear_downloads_cache
from YMusic.core import userbot
from YMusic.misc import SUDOERS
import aiohttp
import json
import config
import requests


PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

STOP_COMMAND = ["STOP"]
PAUSE_COMMAND = ["PAUSE"]
RESUME_COMMAND = ["RESUME"]
LOOP_COMMAND = ["LOOP"]
LOOPEND_COMMAND = ["ENDLOOP"]
ADDSUDO_COMMAND = ["ADDSUDO"]
REMOVESUDO_COMMAND = ["REMOVESUDO"]
SETMAXDURATION_COMMAND = ["SETMAXDURATION", "SMD"]
NANDO_COMMAND = ["NANDO"]
LYRIC_COMMAND = ["LYRIC"]
LLAMA_COMMAND = ["NANDOS"]

def add_sudo(user_id: int):
    global SUDOERS
    SUDOERS.add(user_id)

def remove_sudo(user_id: int):
    global SUDOERS
    if user_id in SUDOERS:
        SUDOERS.remove(user_id)

@app.on_message(filters.command(STOP_COMMAND, PREFIX))
async def _stop(_, message):
    # Get administrators
    administrators = []
    async for m in app.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m)
    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [
        admin.user.id for admin in administrators
    ]:
        Text = await userbot.stop(message.chat.id)
        try:
            clear_queue(message.chat.id)
            await clear_downloads_cache()
        except:
            pass
        await message.reply_text(Text)
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )

@app.on_message(filters.command(PAUSE_COMMAND, PREFIX))
async def _pause(_, message):
    # Get administrators
    administrators = []
    async for m in app.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m)
    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [
        admin.user.id for admin in administrators
    ]:
        Text = await userbot.pause(message.chat.id)
        await message.reply_text(Text)
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )


@app.on_message(filters.command(RESUME_COMMAND, PREFIX))
async def _resume(_, message):
    # Get administrators
    administrators = []
    async for m in app.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m)
    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [
        admin.user.id for admin in administrators
    ]:
        Text = await userbot.resume(message.chat.id)
        await message.reply_text(Text)
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )


@app.on_message(filters.command(LOOP_COMMAND, PREFIX))
async def _loop(_, message):
    administrators = []
    async for m in app.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m)
    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [
        admin.user.id for admin in administrators
    ]:
        loop = await get_loop(message.chat.id)
        if loop == 0:
            try:
                await set_loop(message.chat.id, 5)
                await message.reply_text(
                    "Loop diaktifkan, lagu saat ini akan diputar 5x"
                )
            except Exception as e:
                return await message.reply_text(f"Error:- <code>{e}</code>")

        else:
            await message.reply_text("Loop sudah diaktifkan")
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )
    
@app.on_message(filters.command(LOOPEND_COMMAND, PREFIX))
async def _endLoop(_, message):

    administrators = []
    async for m in app.get_chat_members(
        message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m)
    if (message.from_user.id) in SUDOERS or (message.from_user.id) in [
        admin.user.id for admin in administrators
    ]:
        loop = await get_loop(message.chat.id)
        if loop == 0:
            await message.reply_text("Loop tidak diaktifkan")
        else:
            try:
                await set_loop(message.chat.id, 0)
                await message.reply_text("Loop dimatikan")
            except Exception as e:
                return await message.reply_text(f"Error:- <code>{e}</code>")
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )

@app.on_message(filters.command(ADDSUDO_COMMAND, PREFIX) & filters.user(config.OWNER_ID))
async def _add_sudo(client, message):
    if len(message.command) != 2:
        await message.reply_text("Penggunaan: .addsudo [user_id]")
        return
    
    try:
        user_id = int(message.command[1])
        if user_id in SUDOERS:
            await message.reply_text(f"User ID {user_id} sudah ada dalam daftar SUDO.")
        else:
            add_sudo(user_id)
            await message.reply_text(f"User ID {user_id} berhasil ditambahkan ke daftar SUDO.")
    except ValueError:
        await message.reply_text("User ID harus berupa angka.")

@app.on_message(filters.command(REMOVESUDO_COMMAND, PREFIX) & filters.user(config.OWNER_ID))
async def _remove_sudo(client, message):
    if len(message.command) != 2:
        await message.reply_text("Penggunaan: .removesudo [user_id]")
        return
    
    try:
        user_id = int(message.command[1])
        if user_id not in SUDOERS:
            await message.reply_text(f"User ID {user_id} tidak ada dalam daftar SUDO.")
        else:
            remove_sudo(user_id)
            await message.reply_text(f"User ID {user_id} berhasil dihapus dari daftar SUDO.")
    except ValueError:
        await message.reply_text("User ID harus berupa angka.")

@app.on_message(filters.command(["SUDOLIST"], PREFIX) & filters.user(config.OWNER_ID))
async def _sudo_list(client, message):
    sudo_list = ", ".join(str(sudo_id) for sudo_id in SUDOERS)
    await message.reply_text(f"Daftar SUDO Users:\n{sudo_list}")
    
@app.on_message(filters.command(SETMAXDURATION_COMMAND, PREFIX) & filters.user(config.OWNER_ID))
async def set_max_duration(client, message):
    if len(message.command) != 2:
        await message.reply_text("Penggunaan: .setmaxduration [durasi dalam menit]")
        return
    
    try:
        new_duration = int(message.command[1])
        if new_duration <= 0:
            await message.reply_text("Durasi harus lebih besar dari 0 menit.")
            return
        
        global MAX_DURATION_MINUTES
        config.MAX_DURATION_MINUTES = new_duration
        await message.reply_text(f"MAX_DURATION_MINUTES berhasil diubah menjadi {new_duration} menit.")
    except ValueError:
        await message.reply_text("Durasi harus berupa angka dalam menit.")

# @app.on_message(filters.command(NANDO_COMMAND, PREFIX))
# async def _nando(_, message):
    # if len(message.command) < 2:
        # await message.reply_text("Penggunaan: .nando [query]")
        # return

    # query = " ".join(message.command[1:])
    # api_url = f"https://api.safone.dev/bard?message={query}"

    # loading_message = await message.reply_text("Tunggu sebentar...")

    # async with aiohttp.ClientSession() as session:
        # try:
            # async with session.get(api_url) as response:
                # if response.status == 200:
                    # data = await response.json()
                    # result = data.get('message', 'No message received from API')
                    
                    # await loading_message.delete()
                    
                    # if len(result) > 4096:
                        # chunks = [result[i:i+4096] for i in range(0, len(result), 4096)]
                        # for chunk in chunks:
                            # await message.reply_text(chunk)
                    # else:
                        # await message.reply_text(result)
                # else:
                    # await loading_message.delete()
                    # await message.reply_text(f"Error: Unable to fetch data from API. Status code: {response.status}")
        # except Exception as e:
            # await loading_message.delete()
            # await message.reply_text(f"An error occurred: {str(e)}")

@app.on_message(filters.command(NANDO_COMMAND, PREFIX))
async def _gemini(_, message):
    if len(message.command) < 2:
        await message.reply_text("Penggunaan: .nando [query]")
        return

    query = " ".join(message.command[1:])
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config.GEMINI_API
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": query
                    }
                ]
            }
        ]
    }

    loading_message = await message.reply_text("Tunggu sebentar...")

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            
            await loading_message.delete()
            
            if len(generated_text) > 4096:
                chunks = [generated_text[i:i+4096] for i in range(0, len(generated_text), 4096)]
                for chunk in chunks:
                    await message.reply_text(chunk)
            else:
                await message.reply_text(generated_text)
        else:
            await loading_message.delete()
            await message.reply_text(f"Error: Unable to fetch data from API. Status code: {response.status_code}")
    except Exception as e:
        await loading_message.delete()
        await message.reply_text(f"An error occurred: {str(e)}")

@app.on_message(filters.command(LYRIC_COMMAND, PREFIX))
async def _nando(_, message):
    if len(message.command) < 2:
        await message.reply_text(f"Penggunaan: .lyric [query]")
        return

    query = " ".join(message.command[1:])
    api_url = f"https://api.safone.dev/lyrics?title={query}"

    loading_message = await message.reply_text("Saya sedang mencarinya...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('lyrics', 'No message received from API')
                    lyrics_text = f"📜 Lirik:\n\n{result}"

                    await loading_message.delete()
                    
                    if len(lyrics_text) > 4096:
                        chunks = [lyrics_text[i:i+4096] for i in range(0, len(lyrics_text), 4096)]
                        for chunk in chunks:
                            await message.reply_text(chunk)
                    else:
                        await message.reply_text(lyrics_text)
                else:
                    await loading_message.delete()
                    await message.reply_text(f"Error: Unable to fetch data from API. Status code: {response.status}")
        except Exception as e:
            await loading_message.delete()
            await message.reply_text(f"An error occurred: {str(e)}")


# @app.on_message(filters.command(LLAMA_COMMAND, PREFIX))
# async def _nando(_, message):
    # if len(message.command) < 2:
        # await message.reply_text("Penggunaan: .lama [query]")
        # return

    # query = " ".join(message.command[1:])
    # final_query = f"{query}. gunakan bahasa indonesia"
    # api_url = f"https://api.safone.dev/llama?message={final_query}"

    # loading_message = await message.reply_text("Tunggu sebentar...")

    # async with aiohttp.ClientSession() as session:
        # try:
            # async with session.get(api_url) as response:
                # if response.status == 200:
                    # data = await response.json()
                    # result = data.get('message', 'No message received from API')
                    
                    # await loading_message.delete()
                    
                    # if len(result) > 4096:
                        # chunks = [result[i:i+4096] for i in range(0, len(result), 4096)]
                        # for chunk in chunks:
                            # await message.reply_text(chunk)
                    # else:
                        # await message.reply_text(result)
                # else:
                   # await loading_message.delete()
                   # await message.reply_text(f"Error: Unable to fetch data from API. Status code: {response.status}")
        # except Exception as e:
            # await loading_message.delete()
            # await message.reply_text(f"An error occurred: {str(e)}")
