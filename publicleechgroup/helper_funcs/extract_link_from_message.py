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

import aiohttp
from pyrogram.types import MessageEntity

from publicleechgroup import LOGGER, Config


def extract_url_from_entity(entities: MessageEntity, text: str):
    url = None
    for entity in entities:
        if entity.type == "text_link":
            url = entity.url
        elif entity.type == "url":
            o = entity.offset
            l = entity.length
            url = text[o: o + l]
    return url


async def extract_link(message, type_o_request):
    custom_file_name = None
    url = None
    youtube_dl_username = None
    youtube_dl_password = None

    if message is None:
        url = None
        custom_file_name = None

    elif message.text is not None:
        if message.text.lower().startswith("magnet:"):
            url = message.text.strip()

        elif "|" in message.text:
            url_parts = message.text.split("|")
            if len(url_parts) == 2:
                url = url_parts[0]
                custom_file_name = url_parts[1]
            elif len(url_parts) == 4:
                url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]

        elif message.entities is not None:
            url = extract_url_from_entity(message.entities, message.text)

        else:
            url = message.text.strip()

    elif message.document is not None:
        if message.document.file_name.lower().endswith(".torrent"):
            url = await message.download()
            custom_file_name = message.caption

    elif message.caption is not None:
        if "|" in message.caption:
            url_parts = message.caption.split("|")
            if len(url_parts) == 2:
                url = url_parts[0]
                custom_file_name = url_parts[1]
            elif len(url_parts) == 4:
                url = url_parts[0]
                custom_file_name = url_parts[1]
                youtube_dl_username = url_parts[2]
                youtube_dl_password = url_parts[3]

        elif message.caption_entities is not None:
            url = extract_url_from_entity(message.caption_entities, message.caption)

        else:
            url = message.caption.strip()

    elif message.entities is not None:
        url = message.text

    # trim blank spaces from the URL
    # might have some issues with #45
    if url is not None:
        url = url.strip()
    if custom_file_name is not None:
        custom_file_name = custom_file_name.strip()
    # https://stackoverflow.com/a/761825/4723940
    if youtube_dl_username is not None:
        youtube_dl_username = youtube_dl_username.strip()
    if youtube_dl_password is not None:
        youtube_dl_password = youtube_dl_password.strip()

    # additional conditional check,
    # here to FILTER out BAD URLs
    LOGGER(__name__).info(Config.TG_OFFENSIVE_API)
    if Config.TG_OFFENSIVE_API is not None:
        try:
            async with aiohttp.ClientSession() as session:
                api_url = Config.TG_OFFENSIVE_API.format(
                    i=url, m=custom_file_name, t=type_o_request
                )
                LOGGER(__name__).info(api_url)
                async with session.get(api_url) as resp:
                    suats = int(resp.status)
                    err = await resp.text()
                    if suats != 200:
                        url = None
                        custom_file_name = err
        except:
            # this might occur in case of a BAD API URL,
            # who knows? :\
            pass

    return url, custom_file_name, youtube_dl_username, youtube_dl_password
