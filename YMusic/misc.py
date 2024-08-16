import time
from pyrogram import filters

from .logging import LOGGER
import config


SUDOERS = filters.user()

_boot_ = time.time()


def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    LOGGER("YMusic").info("SUDO USERS LOADED")
