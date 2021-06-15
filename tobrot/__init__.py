#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# the logging things
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import aria2p

# fmt: off
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)
# fmt: on

BOT_START_TIME = time.time()

if os.path.exists("PublicLeech.log"):
    with open("PublicLeech.log", "r+") as f_d:
        f_d.truncate(0)

# the logging things
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "PublicLeech.log",
            maxBytes=50000000,
            backupCount=10,
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("PIL.Image").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


class Config:
    # <----- MANDATORY ENV VARIABLES -----> #
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    AUTH_CHATS = os.environ.get("AUTH_CHATS", -100)
    if os.environ.get("AUTH_CHATS"):
        AUTH_CHATS = list(map(int, os.environ.get("AUTH_CHATS").split()))

    AUTH_USERS = os.environ.get("AUTH_USERS", 183075619)
    if os.environ.get("AUTH_USERS"):
        AUTH_USERS = list(map(int, os.environ.get("AUTH_USERS").split()))

    # <----- OPTIONAL ENV VARIABLES -----> #
    DEFAULT_THUMBNAIL = os.environ.get(
        "DEFAULT_THUMBNAIL", "https://telegra.ph/file/8b973b270f4f380a427b1.png"
    )
    DIS_ABLE_ST_GFC_COMMAND_I = os.environ.get("DIS_ABLE_ST_GFC_COMMAND_I", False)
    DOWNLOAD_LOCATION = os.environ.get(
        "DOWNLOAD_LOCATION", os.path.join(os.getcwd(), "DOWNLOADS")
    )
    EDIT_SLEEP_TIME_OUT = int(os.environ.get("EDIT_SLEEP_TIME_OUT", 5))
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 2097152000))
    MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_MESSAGE_LENGTH", 4096))
    MAX_SPLIT_SIZE = int(os.environ.get("MAX_SPLIT_SIZE", 1900000000))
    PROCESS_MAX_TIMEOUT = int(os.environ.get("PROCESS_MAX_TIMEOUT", 3600))
    RCLONE_CONF_URI = os.environ.get("RCLONE_CONF_URI", None)
    RCLONE_DEST = os.environ.get("RCLONE_DEST", "/PublicLeech")
    BUTTONS_MODE = os.environ.get("BUTTONS_MODE", False)
    SPLIT_ALGORITHM = os.environ.get("SPLIT_ALGORITHM", "hjs")
    # add offensive API
    TG_OFFENSIVE_API = os.environ.get("TG_OFFENSIVE_API", None)
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR", "█")
    UN_FINISHED_PROGRESS_STR = os.environ.get("UN_FINISHED_PROGRESS_STR", "░")


class Command:
    # <----- COMMAND VARIABLES -----> #
    CANCEL = os.environ.get("C_CANCEL", "cancel")
    CLEARTHUMBNAIL = os.environ.get("C_CLEARTHUMBNAIL", "clearthumbnail")
    EVAL = os.environ.get("C_EVAL", "eval")
    EXEC = os.environ.get("C_EXEC", "exec")
    GET_RCLONE_CONF_URI = os.environ.get("C_GET_RCLONE_CONF_URI", "getrcloneconfuri")
    HELP = os.environ.get("C_HELP", "help")
    LEECH = os.environ.get("C_LEECH", "leech")
    PURGE = os.environ.get("C_PURGE", "purge")
    RENAME = os.environ.get("C_RENAME", "rename")
    SAVETHUMBNAIL = os.environ.get("C_SAVETHUMBNAIL", "savethumbnail")
    STATUS = os.environ.get("C_STATUS", "status")
    UPLOAD = os.environ.get("C_UPLOAD", "upload")
    UPLOAD_LOG_FILE = os.environ.get("C_UPLOAD_LOG_FILE", "log")
    YTDL = os.environ.get("C_YTDL", "ytdl")


class String:
    # <----- STRINGS VARIABLES -----> #
    CLEARED_THUMBNAIL = os.environ.get(
        "S_CLEARED_THUMBNAIL", "✅ Custom thumbnail cleared succesfully."
    )
    HELP_MESSAGE = os.environ.get(
        "S_HELP_MESSAGE",
        "please read the <a href='https://t.me/c/1434259219/99'>Pinned Message</a>",
    )
    HELP_SAVE_THUMBNAIL = os.environ.get(
        "S_HELP_SAVE_THUMBNAIL", "Reply to a photo to save custom thumbnail"
    )
    NO_TOR_STATUS = os.environ.get(
        "S_NO_TOR_STATUS", "🤷‍♂️ No Active, Queued or Paused TORRENTs"
    )
    PROCESSING = os.environ.get("S_PROCESSING", "processing ...")
    SAVED_THUMBNAIL = os.environ.get(
        "S_SAVED_THUMBNAIL",
        "Custom video / file thumbnail saved. This image will be used in the upload, till /clearthumbnail.",
    )
    TGD_YTLD_STOOPID_DRUSER = os.environ.get(
        "TGD_YTLD_STOOPID_DRUSER", "😡😡 i can't process this expired request 😏"
    )
    TOR_CANCEL_FAILED = os.environ.get("S_TOR_CANCEL_FAILED", "<i>FAILED</i>\n\n#error")
    TOR_CANCELLED = os.environ.get("S_TOR_CANCELLED", "Leech Cancelled")
    WRONG_MESSAGE = os.environ.get(
        "S_WRONG_MESSAGE", "current CHAT ID: <code>{CHAT_ID}</code>"
    )
