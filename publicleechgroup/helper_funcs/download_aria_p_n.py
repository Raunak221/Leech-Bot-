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
import configparser
import os

from pyrogram.errors import FloodWait, MessageNotModified

from publicleechgroup import LOGGER, Config
from publicleechgroup.helper_funcs.rclone_handler import (
    copy_via_rclone,
    get_r_clone_config,
)
from publicleechgroup.helper_funcs.split_archive_handler import create_archive
from publicleechgroup.helper_funcs.upload_to_tg import upload_to_tg


def add_magnet(aria_instance, magnetic_link, c_file_name):
    options = None
    # if c_file_name is not None:
    #     options = {
    #         "dir": c_file_name
    #     }
    try:
        download = aria_instance.add_magnet(magnetic_link, options)
    except Exception as e:
        return (
            False,
            "<b>FAILED</b> \n"
            + str(e)
            + " \nPlease do not send SLOW links. Read /help",
        )
    else:
        return True, "" + download.gid + ""


def add_torrent(aria_instance, torrent_file_path):
    if torrent_file_path is None:
        return (
            False,
            "<b>FAILED</b> \n\nsomething wrongings when trying to add <u>TORRENT</u> file",
        )
    if os.path.exists(torrent_file_path):
        # Add Torrent Into Queue
        try:
            download = aria_instance.add_torrent(
                torrent_file_path, uris=None, options=None, position=None
            )
        except Exception as e:
            return (
                False,
                "<b>FAILED</b> \n"
                + str(e)
                + " \nPlease do not send SLOW links. Read /help",
            )
        else:
            return True, "" + download.gid + ""
    else:
        return False, "<b>FAILED</b> \n\nPlease try other sources to get workable link"


def add_url(aria_instance, text_url, c_file_name):
    options = None
    # if c_file_name is not None:
    #     options = {
    #         "dir": c_file_name
    #     }
    uris = [text_url]
    # Add URL Into Queue
    try:
        download = aria_instance.add_uris(uris, options)
    except Exception as e:
        return (
            False,
            "<b>FAILED</b> \n"
            + str(e)
            + " \nPlease do not send SLOW links. Read /help",
        )
    else:
        return True, "" + download.gid + ""


async def fake_etairporpa_call(
    aria_instance,
    incoming_link,
    c_file_name,
    sent_message_to_update_tg_p,
    r_clone_header_xedni,
):
    # TODO: duplicate code -_-
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif os.path.isfile(incoming_link) and incoming_link.lower().endswith(".torrent"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    LOGGER(__name__).info(err_message)
    # https://stackoverflow.com/a/58213653/4723940
    await check_progress_for_dl(
        aria_instance, err_message, sent_message_to_update_tg_p, None
    )
    has_metadata = aria_instance.client.tell_status(err_message, ["followedBy"])
    if has_metadata:
        err_message = has_metadata["followedBy"][0]
        await check_progress_for_dl(
            aria_instance, err_message, sent_message_to_update_tg_p, None
        )
    await asyncio.sleep(1)
    file = aria_instance.get_download(err_message)
    to_upload_file = file.name
    # -_-
    r_clone_conf_file = await get_r_clone_config(
        Config.RCLONE_CONF_URI, sent_message_to_update_tg_p._client
    )
    if r_clone_conf_file is not None:  # how? even :\
        config = configparser.ConfigParser()
        config.read(r_clone_conf_file)
        remote_names = config.sections()
        try:
            required_remote = remote_names[r_clone_header_xedni]
        except IndexError:
            return False, "maybe a bug, but index seems not valid"
        remote_file_link = await copy_via_rclone(
            to_upload_file,
            required_remote,
            Config.RCLONE_DEST,  # rclone destination folder
            r_clone_conf_file,
        )
        await sent_message_to_update_tg_p.reply_text(
            "files might be uploaded in the desired remote "
            "please check Logs for any errors"
            f"\n\n{remote_file_link}"
        )
        return True, None


async def call_apropriate_function(
    aria_instance, incoming_link, c_file_name, sent_message_to_update_tg_p, is_zip
):
    if incoming_link.lower().startswith("magnet:"):
        sagtus, err_message = add_magnet(aria_instance, incoming_link, c_file_name)
    elif os.path.isfile(incoming_link) and incoming_link.lower().endswith(".torrent"):
        sagtus, err_message = add_torrent(aria_instance, incoming_link)
    else:
        sagtus, err_message = add_url(aria_instance, incoming_link, c_file_name)
    if not sagtus:
        return sagtus, err_message
    LOGGER(__name__).info(err_message)
    # https://stackoverflow.com/a/58213653/4723940
    await check_progress_for_dl(
        aria_instance, err_message, sent_message_to_update_tg_p, None
    )
    has_metadata = aria_instance.client.tell_status(err_message, ["followedBy"])
    if has_metadata:
        err_message = has_metadata["followedBy"][0]
        await check_progress_for_dl(
            aria_instance, err_message, sent_message_to_update_tg_p, None
        )
    await asyncio.sleep(1)
    file = aria_instance.get_download(err_message)
    to_upload_file = file.name
    """os.path.join(
        c_file_name,
        file.name
    )"""
    #
    if is_zip:
        # first check if current free space allows this
        # ref: https://github.com/out386/aria-telegram-mirror-bot/blob/master/src/download_tools/aria-tools.ts#L194
        # archive the contents
        check_if_file = await create_archive(to_upload_file)
        if check_if_file is not None:
            to_upload_file = check_if_file
    #
    response = {}
    LOGGER(__name__).info(response)
    user_id = sent_message_to_update_tg_p.reply_to_message.from_user.id
    final_response = await upload_to_tg(
        sent_message_to_update_tg_p, to_upload_file, user_id, response
    )
    LOGGER(__name__).info(final_response)
    message_to_send = ""
    for key_f_res_se in final_response:
        local_file_name = key_f_res_se
        message_id = final_response[key_f_res_se]
        channel_id = str(sent_message_to_update_tg_p.chat.id)[4:]
        private_link = f"https://t.me/c/{channel_id}/{message_id}"
        message_to_send += "👉 <a href='"
        message_to_send += private_link
        message_to_send += "'>"
        message_to_send += local_file_name
        message_to_send += "</a>"
        message_to_send += "\n"
    if message_to_send != "":
        mention_req_user = (
            f"<a href='tg://user?id={user_id}'>Your Requested Files</a>\n\n"
        )
        message_to_send = mention_req_user + message_to_send
        message_to_send = message_to_send + "\n\n" + "#uploads"
    else:
        message_to_send = "<i>FAILED</i> to upload files. 😞😞"
    await sent_message_to_update_tg_p.reply_to_message.reply_text(
        text=message_to_send, quote=True, disable_web_page_preview=True
    )
    return True, None


# https://github.com/jaskaranSM/UniBorg/blob/6d35cf452bce1204613929d4da7530058785b6b1/stdplugins/aria.py#L136-L164
async def check_progress_for_dl(aria2, gid, event, previous_message):
    try:
        file = aria2.get_download(gid)
        complete = file.is_complete
        if not complete:
            if not file.error_message:
                # sometimes, this weird https://t.me/c/1220993104/392975
                # error creeps up
                # TODO: temporary workaround
                downloading_dir_name = "N/A"
                try:
                    # another derp -_-
                    # https://t.me/c/1220993104/423318
                    downloading_dir_name = str(file.name)
                except:
                    pass
                #
                msg = f"\nFilename: <i>{downloading_dir_name}</i>"
                msg += (
                    f"\nProgress: {file.progress_string()} of "
                    f"<b>{file.total_length_string()}</b> at "
                    f"{file.download_speed_string()}, "
                    f"ETA: {file.eta_string()}"
                )
                msg += f"\n<b>Info:</b> P: {file.connections}"
                if file.seeder is False:
                    """https://t.me/c/1220993104/670177"""
                    msg += f" || S: {file.num_seeders}"
                # msg += f"\nStatus: {file.status}"
                msg += f"\n<code>/cancel {gid}</code>"
                # LOGGER.info(msg)
                if msg != previous_message:
                    await event.edit(msg)
                    previous_message = msg
            else:
                msg = file.error_message
                await event.edit(f"<code>{msg}</code>")
                return False
            await asyncio.sleep(Config.EDIT_SLEEP_TIME_OUT)
            return await check_progress_for_dl(aria2, gid, event, previous_message)
        else:
            await event.edit(f"File Downloaded Successfully: <code>{file.name}</code>")
            return True
    except MessageNotModified:
        pass
    except FloodWait as e:
        await asyncio.sleep(e.x)
    except RecursionError:
        file.remove(force=True)
        await event.edit(
            "Download Auto Canceled :\n\n"
            "Your Torrent/Link {} is Dead.".format(file.name)
        )
        return False
    except Exception as e:
        LOGGER(__name__).info(str(e))
        if " not found" in str(e) or "'file'" in str(e):
            await event.edit("Download Canceled :\n<code>{}</code>".format(file.name))
        else:
            LOGGER(__name__).info(str(e))
            await event.edit(
                "<u>error</u> :\n<code>{}</code> \n\n#error".format(str(e))
            )
        return False


# https://github.com/jaskaranSM/UniBorg/blob/6d35cf452bce1204613929d4da7530058785b6b1/stdplugins/aria.py#L136-L164
