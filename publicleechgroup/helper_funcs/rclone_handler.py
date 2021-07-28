#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  PublicLeech
#  Copyright (C) 2020 The Authors

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
import re
from typing import Optional

from pyrogram import Client
from pyrogram.errors import ChannelInvalid

from publicleechgroup import LOGGER
from publicleechgroup.helper_funcs.utils import run_command


async def copy_via_rclone(src: str, remote_name: str, remote_dir: str, conf_file: str):
    if os.path.isdir(src):
        remote_dir = f"{remote_dir}/{src}"
    command_to_exec = [
        "rclone",
        "move",
        src,
        f"{remote_name}:{remote_dir}",
        f"--config={conf_file}",
        "--fast-list",
        "--transfers",
        "18",
        "--checkers",
        "10",
        "--drive-chunk-size",
        "64M",
    ]
    LOGGER(__name__).info(command_to_exec)
    t_response, e_response = await run_command(command_to_exec)
    # Wait for the subprocess to finish
    LOGGER(__name__).info(e_response)
    LOGGER(__name__).info(t_response)
    # https://github.com/rg3/youtube-dl/issues/2630#issuecomment-38635239
    remote_file_link = await r_clone_extract_link_s(
        re.escape(src), remote_name, remote_dir, conf_file
    )
    LOGGER(__name__).info(remote_file_link)
    return remote_file_link


async def get_r_clone_config(message_link: str, py_client: Client) -> Optional[str]:
    config_path = os.path.join(os.getcwd(), ".config", "rclone", "rclone.conf")
    if os.path.exists(config_path):
        return config_path
    splited_uri = message_link.split("/")
    chat_id, message_id = None, None
    if len(splited_uri) == 6 and splited_uri[3] == "c":
        chat_id, message_id = int(splited_uri[4]), int(splited_uri[5])
    try:
        conf_mesg = await py_client.get_messages(
            chat_id=chat_id, message_ids=message_id
        )
    except ChannelInvalid:
        LOGGER(__name__).info("invalid RClone config URL. this is NOT an ERROR")
        return None
    return await py_client.download_media(message=conf_mesg, file_name=config_path)


async def r_clone_extract_link_s(
    src_file_name: str, remote_name: str, remote_dir: str, conf_file: str
):
    # TODO: Need to fix file linking for individual files
    command_to_exec = [
        "rclone",
        "link",
        f"{remote_name}:{remote_dir}",
        f"--config={conf_file}",
    ]
    LOGGER(__name__).info(command_to_exec)
    t_response, e_response = await run_command(command_to_exec)
    # Wait for the subprocess to finish
    LOGGER(__name__).info(e_response)
    LOGGER(__name__).info(t_response)
    return t_response


async def save_rclone_conf_f(_, message):
    reply = message.reply_to_message
    username = reply.chat.username
    if reply and (not username or message.chat.type == "private"):
        rclone_uri = f"https://t.me/c/{reply.chat.id}/{reply.message_id}"
        await message.reply_text(
            f"Set <code>RCLONE_CONF_URI</code> with <code>{rclone_uri}</code>"
        )
    else:
        await message.reply_text(
            "Forward your rclone.conf to a private space and retry/reply this command\n\n"
            "<b>please DO NOT upload confidential credentials, in public groups.</b>"
        )
        return
