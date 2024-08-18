from pyrogram import filters
from pyrogram.enums import ChatMembersFilter

from YMusic import app
from YMusic.utils.queue import clear_queue
from YMusic.utils.loop import get_loop, set_loop
from YMusic.utils.utils import clear_downloads_cache
from YMusic.core import userbot
from YMusic.misc import SUDOERS

import config

PREFIX = config.PREFIX
RPREFIX = config.RPREFIX

STOP_COMMAND = ["STOP"]
PAUSE_COMMAND = ["PAUSE"]
RESUME_COMMAND = ["RESUME"]
LOOP_COMMAND = ["LOOP", "L"]
LOOPEND_COMMAND = ["ENDLOOP", "EL"]
ADDSUDO_COMMAND = ["ADDSUDO"]
REMOVESUDO_COMMAND = ["REMOVESUDO"]
SETMAXDURATION_COMMAND = ["SETMAXDURATION", "SMD"]

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
            clear_downloads_cache()
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
                    "Loop diaktifkan, lagu akan diputar 5x"
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

