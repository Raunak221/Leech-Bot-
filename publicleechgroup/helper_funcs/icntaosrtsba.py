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

from pyrogram.types import Message

from publicleechgroup import LOGGER, Config, aria2
from publicleechgroup.helper_funcs.download_aria_p_n import (
    call_apropriate_function,
    fake_etairporpa_call,
)
from publicleechgroup.helper_funcs.extract_link_from_message import extract_link
from publicleechgroup.helper_funcs.fix_tcerrocni_images import proc_ess_image_aqon
from publicleechgroup.helper_funcs.youtube_dl_extractor import (
    extract_youtube_dl_formats,
)


async def leech_btn_k(message: Message, cb_data: str):
    # get link from the incoming message
    dl_url, cf_name, _, _ = await extract_link(message.reply_to_message, "LEECH")
    LOGGER(__name__).info(f"extracted /leech links {dl_url}")
    # LOGGER.info(cf_name)
    current_user_id = message.reply_to_message.from_user.id
    # create an unique directory
    new_download_location = os.path.join(
        Config.DOWNLOAD_LOCATION,
        str(current_user_id),
        str(message.reply_to_message.message_id),
    )
    # create download directory, if not exist
    if not os.path.isdir(new_download_location):
        os.makedirs(new_download_location)
    if dl_url is not None:
        if "_" in cb_data:
            LOGGER(__name__).info("rclone upload mode")
            # try to download the "link"
            sagtus, err_message = await fake_etairporpa_call(
                aria2,
                dl_url,
                new_download_location,
                message,
                int(cb_data.split("_")[2])
                # maybe IndexError / ValueError might occur,
                # we don't know, yet!!
            )
        else:
            is_zip = False
            if "a" in cb_data:
                is_zip = True
            LOGGER(__name__).info("tg upload mode")
            # try to download the "link"
            sagtus, err_message = await call_apropriate_function(
                aria2, dl_url, new_download_location, message, is_zip
            )
        if not sagtus:
            # if FAILED, display the error message
            await message.edit_text(err_message)


async def ytdl_btn_k(message: Message):
    i_m_sefg = await message.edit_text("processing")
    # LOGGER(__name__).info(message)
    # extract link from message
    dl_url, cf_name, yt_dl_user_name, yt_dl_pass_word = await extract_link(
        message.reply_to_message, "YTDL"
    )
    LOGGER(__name__).info(f"extracted /ytdl links {dl_url}")
    # LOGGER.info(cf_name)
    if dl_url is not None:
        current_user_id = message.reply_to_message.from_user.id
        # create an unique directory
        user_working_dir = os.path.join(
            Config.DOWNLOAD_LOCATION,
            str(current_user_id),
            str(message.reply_to_message.message_id),
        )
        # create download directory, if not exist
        if not os.path.isdir(user_working_dir):
            os.makedirs(user_working_dir)
        LOGGER(__name__).info("fetching youtube_dl formats")
        # list the formats, and display in button markup formats
        thumb_image, text_message, reply_markup = await extract_youtube_dl_formats(
            dl_url,
            # cf_name,
            yt_dl_user_name,
            yt_dl_pass_word,
            user_working_dir,
        )
        if thumb_image:
            thumb_image = await proc_ess_image_aqon(thumb_image, user_working_dir)
            await message.reply_photo(
                photo=thumb_image,
                quote=True,
                caption=text_message,
                reply_to_message_id=message.reply_to_message.message_id,
                reply_markup=reply_markup,
            )
            os.remove(thumb_image)
            await i_m_sefg.delete()
        else:
            await i_m_sefg.edit_text(text=text_message, reply_markup=reply_markup)
    else:
        await i_m_sefg.delete()
