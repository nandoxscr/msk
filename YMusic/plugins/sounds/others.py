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
LOOP_COMMAND = ["LOOP"]
LOOPEND_COMMAND = ["ENDLOOP"]


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
    # Get administrators
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
                    "Loop enabled. Now current song will be played 5 times"
                )
            except Exception as e:
                return await message.reply_text(f"Error:- <code>{e}</code>")

        else:
            await message.reply_text("Loop already enabled")
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )


@app.on_message(filters.command(LOOPEND_COMMAND, PREFIX))
async def _endLoop(_, message):
    # Get administrators
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
            await message.reply_text("Lopp is not enabled")
        else:
            try:
                await set_loop(message.chat.id, 0)
                await message.reply_text("Loop Disabled")
            except Exception as e:
                return await message.reply_text(f"Error:- <code>{e}</code>")
    else:
        return await message.reply_text(
            "Hanya Admin Saja"
        )
