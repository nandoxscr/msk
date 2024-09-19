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
import re

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

@app.on_message(filters.command(NANDO_COMMAND, PREFIX))
async def _nando(_, message):
    if len(message.command) < 2:
        await message.reply_text("Penggunaan: .nando [query]")
        return

    query = " ".join(message.command[1:])
    loading_message = await message.reply_text("Tunggu sebentar...")

    try:
        result = await get_respon(query)
        
        await loading_message.delete()
        
        if len(result) > 4096:
            chunks = [result[i:i+4096] for i in range(0, len(result), 4096)]
            for chunk in chunks:
                await message.reply_text(chunk)
        else:
            await message.reply_text(result)
    except Exception as e:
        await loading_message.delete()
        await message.reply_text(f"An error occurred: {str(e)}")

async def get_respon(user_input):
    url = "https://api.stack-ai.com/inference/v0/stream/b01daf4e-b4b1-4444-a6c3-c8bdb9516fb2/66581edf4c58badf56ab93cb?sse=true"
    header = {
        "Host": "api.stack-ai.com",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.10.0",
        "Authorization": f"Bearer {config.STACK_AI_BEARER_TOKEN}"
    }
    data = {"in-0": user_input, "in-1": ""}
    
    resp = requests.post(url, headers=header, json=data, stream=True)
    if resp.status_code != 200:
        return f"Gagal dengan kode status {resp.status_code}"

    hasil = ""
    for baris in resp.iter_lines():
        decoded_line = baris.decode('utf-8')
        match = re.search(r'"out-0":"(.*?)"', decoded_line)
        if match:
            hasil += match.group(1)

    return hasil
