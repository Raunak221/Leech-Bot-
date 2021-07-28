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

from publicleechgroup import LOGGER, Command, Config, aria2
from publicleechgroup.helper_funcs.create_r_o_m import get_markup
from publicleechgroup.helper_funcs.download_aria_p_n import (
    call_apropriate_function,
    fake_etairporpa_call,
)
from publicleechgroup.helper_funcs.extract_link_from_message import extract_link
from publicleechgroup.helper_funcs.utils import fetch_thumbnail
from publicleechgroup.helper_funcs.youtube_dl_extractor import (
    extract_youtube_dl_formats,
)


async def incoming_purge_message_f(client, message):
    """/purge command"""
    i_m_sefg2 = await message.reply_text("Purging...", quote=True)
    if message.from_user.id in Config.AUTH_USERS:
        try:
            aria2.remove_all(force=True)
            await i_m_sefg2.edit_text("Purged!")
        except False:
            await i_m_sefg2.edit_text("Purge failed")


async def incoming_message_f(client, message):
    """/leech command"""
    i_m_sefg = await message.reply_text("checking ", quote=True)
    t_, rm_ = await get_markup(message)
    await i_m_sefg.edit_text(text=t_, reply_markup=rm_, disable_web_page_preview=True)


async def leech_commandi_f(client, message):
    m_ = await message.reply_text("checking", quote=True)
    m_sgra = " ".join(message.command[1:])
    if not message.reply_to_message:
        await m_.edit_text(
            "No URIs to download\n" f"Reply <code>/{Command.LEECH}</code> to an URI"
        )
        return
    # get link from the incoming message
    dl_url, cf_name, _, _ = await extract_link(message.reply_to_message, "LEECH")
    LOGGER(__name__).info(f"extracted /leech links {dl_url}")
    # LOGGER.info(cf_name)
    if dl_url is not None:
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
        if "_" in m_sgra:
            LOGGER(__name__).info("rclone upload mode")
            # try to download the "link"
            sagtus, err_message = await fake_etairporpa_call(
                aria2,
                dl_url,
                new_download_location,
                m_,
                int(m_sgra.split("_")[2])
                # maybe IndexError / ValueError might occur,
                # we don't know, yet!!
            )
        else:
            is_zip = False
            if "a" in m_sgra:
                is_zip = True
            LOGGER(__name__).info("tg upload mode")
            # try to download the "link"
            sagtus, err_message = await call_apropriate_function(
                aria2, dl_url, new_download_location, m_, is_zip
            )
        if not sagtus:
            # if FAILED, display the error message
            await m_.edit_text(err_message)


async def incoming_youtube_dl_f(client, message):
    """/ytdl command"""
    i_m_sefg = await message.reply_text("processing", quote=True)
    # LOGGER.info(message)
    if not message.reply_to_message:
        await i_m_sefg.edit_text(
            "No ytdl links to download\n"
            f"Reply <code>/{Command.YTDL}</code> to a ytdl link"
        )
        return
    # extract link from message
    dl_url, cf_name, yt_dl_user_name, yt_dl_pass_word = await extract_link(
        message.reply_to_message, "YTDL"
    )
    LOGGER(__name__).info(f"extracted /ytdl links {dl_url}")
    # LOGGER.info(cf_name)
    if dl_url is not None:
        current_user_id = message.from_user.id
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
        if thumb_image is not None:
            thumb_image = await fetch_thumbnail(thumb_image, user_working_dir)
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
