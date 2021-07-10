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

import configparser

from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton, Message

from publicleechgroup import Config
from publicleechgroup.helper_funcs.rclone_handler import get_r_clone_config


async def get_markup(message: Message):
    ikeyboard = InlineKeyboard()
    ikeyboard.row(
        InlineKeyboardButton("leech", callback_data="leech"),
        InlineKeyboardButton("yt-dlp", callback_data="ytdl"),
    )
    ikeyboard.row(
        InlineKeyboardButton("leech archive", callback_data="leecha"),
        InlineKeyboardButton("yt-dlp archive", callback_data="ytdla"),
    )
    if Config.RCLONE_CONF_URI:
        r_clone_conf_file = await get_r_clone_config(
            Config.RCLONE_CONF_URI, message._client
        )
        if r_clone_conf_file is not None:
            config = configparser.ConfigParser()
            config.read(r_clone_conf_file)
            remote_names = config.sections()
            for it_r, remote_name in enumerate(remote_names):
                ikeyboard.row(
                    InlineKeyboardButton(
                        f"RClone LEECH {remote_name}",
                        callback_data=f"leech_rc_{it_r}".encode("UTF-8"),
                    )
                )
    reply_text = "please select the required option"
    return reply_text, ikeyboard
