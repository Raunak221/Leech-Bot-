#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  Copyright (C) 2020 PublicLeech Authors

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil

from pyrogram import Client, __version__, filters
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

from publicleechgroup import LOGGER, Command, Config
from publicleechgroup.helper_funcs.custom_filters import message_fliter
from publicleechgroup.helper_funcs.rclone_handler import save_rclone_conf_f
from publicleechgroup.plugins.call_back_button_handler import button
from publicleechgroup.plugins.custom_thumbnail import clear_thumb_nail, save_thumb_nail
from publicleechgroup.plugins.incoming_message_fn import (
    incoming_message_f,
    incoming_purge_message_f,
    incoming_youtube_dl_f,
    leech_commandi_f,
)
from publicleechgroup.plugins.new_join_fn import help_message_f, new_join_f
from publicleechgroup.plugins.status_message_fn import (
    cancel_message_f,
    eval_message_f,
    exec_message_f,
    status_message_f,
    upload_document_f,
    upload_log_file,
)


class Bot(Client):
    """modded client"""

    def __init__(self):
        super().__init__(
            ":memory:",
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            workers=343,
            workdir=Config.DOWNLOAD_LOCATION,
            parse_mode="html",
            sleep_threshold=1800,
            # TODO: utilize PSP
            # plugins={
            #     "root": "bot/plugins"
            # }
        )

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()

        # create download directory, if not exist
        if not os.path.isdir(Config.DOWNLOAD_LOCATION):
            os.makedirs(Config.DOWNLOAD_LOCATION)

        LOGGER(__name__).info("@PublicLeechGroup, trying to add handlers")
        # PURGE command
        self.add_handler(
            MessageHandler(
                incoming_purge_message_f,
                filters=filters.command([Command.PURGE])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        # STATUS command
        self.add_handler(
            MessageHandler(
                status_message_f,
                filters=filters.command([Command.STATUS])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        # CANCEL command
        self.add_handler(
            MessageHandler(
                cancel_message_f,
                filters=filters.command([Command.CANCEL])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        if not Config.BUTTONS_MODE:
            LOGGER(__name__).info("using COMMANDi mode")
            # LEECH command
            self.add_handler(
                MessageHandler(
                    leech_commandi_f,
                    filters=filters.command([Command.LEECH])
                    & filters.chat(chats=Config.AUTH_CHATS),
                )
            )

            # YTDL command
            self.add_handler(
                MessageHandler(
                    incoming_youtube_dl_f,
                    filters=filters.command([Command.YTDL])
                    & filters.chat(chats=Config.AUTH_CHATS),
                )
            )
        else:
            LOGGER(__name__).info("using BUTTONS mode")
            # all messages filter
            # in the AUTH_CHATS
            self.add_handler(
                MessageHandler(
                    incoming_message_f,
                    filters=message_fliter & filters.chat(chats=Config.AUTH_CHATS),
                )
            )

        # button is LEGACY command to handle
        # the OLD YTDL buttons,
        # and also the new SUB buttons
        self.add_handler(CallbackQueryHandler(button))

        self.add_handler(
            MessageHandler(
                exec_message_f,
                filters=filters.command([Command.EXEC])
                & filters.user(users=Config.AUTH_USERS),
            )
        )

        self.add_handler(
            MessageHandler(
                eval_message_f,
                filters=filters.command([Command.EVAL])
                & filters.user(users=Config.AUTH_USERS),
            )
        )

        # MEMEs COMMANDs
        self.add_handler(
            MessageHandler(
                upload_document_f,
                filters=filters.command([Command.UPLOAD])
                & filters.user(users=Config.AUTH_USERS),
            )
        )

        # HELP command
        self.add_handler(
            MessageHandler(
                help_message_f,
                filters=filters.command([Command.HELP])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        # not AUTH CHANNEL users
        self.add_handler(
            MessageHandler(new_join_f, filters=~filters.chat(chats=Config.AUTH_CHATS))
        )

        # welcome MESSAGE
        self.add_handler(
            MessageHandler(
                help_message_f,
                filters=filters.chat(chats=Config.AUTH_CHATS)
                & filters.new_chat_members,
            )
        )

        # savethumbnail COMMAND
        self.add_handler(
            MessageHandler(
                save_thumb_nail,
                filters=filters.command([Command.SAVETHUMBNAIL])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        # clearthumbnail COMMAND
        self.add_handler(
            MessageHandler(
                clear_thumb_nail,
                filters=filters.command([Command.CLEARTHUMBNAIL])
                & filters.chat(chats=Config.AUTH_CHATS),
            )
        )

        # an probably easy way to get RClone CONF URI
        self.add_handler(
            MessageHandler(
                save_rclone_conf_f,
                filters=filters.command([Command.GET_RCLONE_CONF_URI])
                & filters.user(users=Config.AUTH_USERS),
            )
        )

        # Telegram command to upload LOG files
        self.add_handler(
            MessageHandler(
                upload_log_file,
                filters=filters.command([Command.UPLOAD_LOG_FILE])
                & filters.user(users=Config.AUTH_USERS),
            )
        )

        LOGGER(__name__).info(
            f"@{usr_bot_me.username} based on Pyrogram v{__version__} "
        )

    async def stop(self, *args):
        await super().stop()
        shutil.rmtree(Config.DOWNLOAD_LOCATION, ignore_errors=True)
        LOGGER(__name__).info("PublicLeechGroup stopped. Bye.")
