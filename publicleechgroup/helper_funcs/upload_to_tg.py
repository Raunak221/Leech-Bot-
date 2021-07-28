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

import asyncio
import math
import os
import time
from shutil import copyfile

import magic
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaAudio, InputMediaDocument, InputMediaVideo

from publicleechgroup import LOGGER, Config
from publicleechgroup.helper_funcs.split_archive_handler import split_large_files
from publicleechgroup.helper_funcs.utils import (
    humanbytes,
    take_screen_shot,
    time_formatter,
)


async def copy_file(input_file, output_dir):
    output_file = os.path.join(output_dir, str(time.time()) + ".jpg")
    # https://stackoverflow.com/a/123212/4723940
    copyfile(input_file, output_file)
    return output_file


async def upload_to_tg(
    message,
    local_file_name,
    from_user,
    dict_contatining_uploaded_files,
    edit_media=False,
    custom_caption=None,
):
    LOGGER(__name__).info(local_file_name)
    base_file_name = os.path.basename(local_file_name)
    caption_str = custom_caption
    if not caption_str or not edit_media:
        LOGGER(__name__).info("fall-back to default file_name")
        caption_str = "<code>"
        caption_str += base_file_name
        caption_str += "</code>"
    # caption_str += "\n\n"
    # caption_str += "<a href='tg://user?id="
    # caption_str += str(from_user)
    # caption_str += "'>"
    # caption_str += "Here is the file to the link you sent"
    # caption_str += "</a>"
    if os.path.isdir(local_file_name):
        directory_contents = os.listdir(local_file_name)
        directory_contents.sort()
        # number_of_files = len(directory_contents)
        LOGGER(__name__).info(directory_contents)
        new_m_esg = message
        if not message.photo:
            new_m_esg = await message.reply_text(
                "Found {} files".format(len(directory_contents)),
                quote=True
                # reply_to_message_id=message.message_id
            )
        for single_file in directory_contents:
            # recursion: will this FAIL somewhere?
            file_path = os.path.join(local_file_name, single_file)
            if not os.path.exists(file_path):
                continue
            await upload_to_tg(
                new_m_esg,
                file_path,
                from_user,
                dict_contatining_uploaded_files,
                edit_media,
                caption_str,
            )
    elif os.path.getsize(local_file_name) > Config.MAX_FILE_SIZE:
        LOGGER(__name__).info("TODO")
        d_f_s = humanbytes(os.path.getsize(local_file_name))
        i_m_s_g = await message.reply_text(
            "Telegram does not support uploading this file.\n"
            f"Detected File Size: {d_f_s} 😡\n"
            "\n🤖 trying to split the files 🌝🌝🌚"
        )
        splitted_dir = await split_large_files(local_file_name)
        totlaa_sleif = os.listdir(splitted_dir)
        totlaa_sleif.sort()
        number_of_files = len(totlaa_sleif)
        LOGGER(__name__).info(totlaa_sleif)
        ba_se_file_name = os.path.basename(local_file_name)
        await i_m_s_g.edit_text(
            f"Detected File Size: {d_f_s} 😡\n"
            f"<code>{ba_se_file_name}</code> splitted into {number_of_files} files.\n"
            "trying to upload to Telegram, now ..."
        )
        for le_file in totlaa_sleif:
            # recursion: will this FAIL somewhere?
            file_path = os.path.join(splitted_dir, le_file)
            if not os.path.isfile(file_path):
                continue
            await upload_to_tg(
                message,
                file_path,
                from_user,
                dict_contatining_uploaded_files,
            )
    else:
        sent_message = None
        if os.path.isfile(local_file_name):
            sent_message = await upload_single_file(
                message, local_file_name, caption_str, from_user, edit_media
            )
        if sent_message is not None:
            dict_contatining_uploaded_files[
                os.path.basename(local_file_name)
            ] = sent_message.message_id
    # await message.delete()
    return dict_contatining_uploaded_files


async def upload_single_file(
    message, local_file_path, caption_str, from_user, edit_media
):
    await asyncio.sleep(Config.EDIT_SLEEP_TIME_OUT)
    start_time = time.time()
    #
    thumbnail_location = os.path.join(
        Config.DOWNLOAD_LOCATION, "thumbnails", str(from_user) + ".jpg"
    )
    LOGGER(__name__).info(thumbnail_location)
    #
    message_for_progress_display = message
    file_name = os.path.basename(local_file_path)
    if not edit_media:
        message_for_progress_display = await message.reply_text(
            f"starting upload of {file_name}"
        )
    thumb_image_path = None
    file_type = magic.from_file(local_file_path, mime=True)
    if file_type.startswith("video/"):
        metadata = extractMetadata(createParser(local_file_path))
        duration = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        #
        width = 0
        height = 0
        if os.path.exists(thumbnail_location):
            thumb_image_path = await copy_file(
                thumbnail_location, os.path.dirname(os.path.abspath(local_file_path))
            )
        else:
            thumb_image_path = await take_screen_shot(
                local_file_path,
                os.path.dirname(os.path.abspath(local_file_path)),
                (duration / 2),
            )
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
        #
        thumb = None
        if thumb_image_path is not None and os.path.isfile(thumb_image_path):
            thumb = thumb_image_path
        # send video
        if edit_media and message.photo:
            sent_message = await message.edit_media(
                media=InputMediaVideo(
                    media=local_file_path,
                    thumb=thumb,
                    caption=caption_str,
                    parse_mode="html",
                    width=width,
                    height=height,
                    duration=duration,
                    supports_streaming=True,
                )
                # quote=True,
            )
        else:
            sent_message = await message.reply_video(
                video=local_file_path,
                # quote=True,
                caption=caption_str,
                parse_mode="html",
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
                supports_streaming=True,
                disable_notification=True,
                # reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    file_name,
                    message_for_progress_display,
                    start_time,
                ),
            )
    elif file_type.startswith("audio/"):
        metadata = extractMetadata(createParser(local_file_path))
        duration = 0
        title = ""
        artist = ""
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("title"):
            title = metadata.get("title")
        if metadata.has("artist"):
            artist = metadata.get("artist")
        if os.path.isfile(thumbnail_location):
            thumb_image_path = await copy_file(
                thumbnail_location, os.path.dirname(os.path.abspath(local_file_path))
            )
        thumb = None
        if thumb_image_path is not None and os.path.isfile(thumb_image_path):
            thumb = thumb_image_path
        # send audio
        if edit_media and message.photo:
            sent_message = await message.edit_media(
                media=InputMediaAudio(
                    media=local_file_path,
                    thumb=thumb,
                    caption=caption_str,
                    parse_mode="html",
                    duration=duration,
                    performer=artist,
                    title=title,
                )
                # quote=True,
            )
        else:
            sent_message = await message.reply_audio(
                audio=local_file_path,
                # quote=True,
                caption=caption_str,
                parse_mode="html",
                duration=duration,
                performer=artist,
                title=title,
                thumb=thumb,
                disable_notification=True,
                # reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    file_name,
                    message_for_progress_display,
                    start_time,
                ),
            )
    else:
        if os.path.isfile(thumbnail_location):
            thumb_image_path = await copy_file(
                thumbnail_location, os.path.dirname(os.path.abspath(local_file_path))
            )
        # if a file, don't upload "thumb"
        # this "diff" is a major derp -_- 😔😭😭
        thumb = None
        if thumb_image_path is not None and os.path.isfile(thumb_image_path):
            thumb = thumb_image_path
        #
        # send document
        if edit_media and message.photo:
            sent_message = await message.edit_media(
                media=InputMediaDocument(
                    media=local_file_path,
                    thumb=thumb,
                    caption=caption_str,
                    parse_mode="html",
                )
                # quote=True,
            )
        else:
            sent_message = await message.reply_document(
                document=local_file_path,
                # quote=True,
                thumb=thumb,
                caption=caption_str,
                parse_mode="html",
                disable_notification=True,
                # reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    file_name,
                    message_for_progress_display,
                    start_time,
                ),
            )
    if thumb is not None:
        os.remove(thumb)
    if message.message_id != message_for_progress_display.message_id:
        await message_for_progress_display.delete()
    os.remove(local_file_path)
    return sent_message


async def progress_for_pyrogram(current, total, filename, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        if elapsed_time == 0:
            return
        speed = current / elapsed_time
        time_to_completion = round((total - current) / speed)
        estimated_total_time = time_formatter(time_to_completion)

        progress_block = "[{}{}]\n".format(
            "".join(
                Config.FINISHED_PROGRESS_STR for _ in range(math.floor(percentage / 5))
            ),
            "".join(
                Config.UN_FINISHED_PROGRESS_STR
                for _ in range(20 - math.floor(percentage / 5))
            ),
        )

        progress_text = (
            f"Filename: <i>{filename}</i>\n"
            f"{progress_block}"
            f"Uploading {round(percentage, 2)}% of "
            f"{humanbytes(total)} @ {humanbytes(speed)}/s, "
            f"ETA: {estimated_total_time}\n"
        )
        try:
            if not message.photo:
                await message.edit_text(text=progress_text)
            else:
                await message.edit_caption(caption=progress_text)
        except FloodWait as e:
            await asyncio.sleep(e.x)
