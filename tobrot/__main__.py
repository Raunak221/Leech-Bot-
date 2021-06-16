#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


import os

from pyrogram import Client, filters
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

from tobrot import LOGGER, Command, Config
from tobrot.helper_funcs.custom_filters import message_fliter
from tobrot.plugins.call_back_button_handler import button
from tobrot.plugins.custom_thumbnail import clear_thumb_nail, save_thumb_nail
from tobrot.plugins.incoming_message_fn import (
    incoming_message_f,
    incoming_purge_message_f,
    incoming_youtube_dl_f,
    leech_commandi_f,
)
from tobrot.plugins.new_join_fn import help_message_f, new_join_f
from tobrot.plugins.status_message_fn import (
    cancel_message_f,
    eval_message_f,
    exec_message_f,
    save_rclone_conf_f,
    status_message_f,
    upload_document_f,
    upload_log_file,
)

if __name__ == "__main__":
    # create download directory, if not exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    #
    app = Client(
        ":memory:",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        workers=343,
        workdir=Config.DOWNLOAD_LOCATION,
    )
    #
    app.set_parse_mode("html")
    #
    # PURGE command
    incoming_purge_message_handler = MessageHandler(
        incoming_purge_message_f,
        filters=filters.command([Command.PURGE])
        & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(incoming_purge_message_handler)

    # STATUS command
    status_message_handler = MessageHandler(
        status_message_f,
        filters=filters.command([Command.STATUS])
        & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(status_message_handler)

    # CANCEL command
    cancel_message_handler = MessageHandler(
        cancel_message_f,
        filters=filters.command([Command.CANCEL])
        & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(cancel_message_handler)

    if not Config.BUTTONS_MODE:
        LOGGER.info("using COMMANDi mode")
        # LEECH command
        incoming_message_handler = MessageHandler(
            leech_commandi_f,
            filters=filters.command([Command.LEECH])
            & filters.chat(chats=Config.AUTH_CHATS),
        )
        app.add_handler(incoming_message_handler)

        # YTDL command
        incoming_youtube_dl_handler = MessageHandler(
            incoming_youtube_dl_f,
            filters=filters.command([Command.YTDL])
            & filters.chat(chats=Config.AUTH_CHATS),
        )
        app.add_handler(incoming_youtube_dl_handler)
    else:
        LOGGER.info("using BUTTONS mode")
        # all messages filter
        # in the AUTH_CHANNELs
        incoming_message_handler = MessageHandler(
            incoming_message_f,
            filters=message_fliter & filters.chat(chats=Config.AUTH_CHATS),
        )
        app.add_handler(incoming_message_handler)

    # button is LEGACY command to handle
    # the OLD YTDL buttons,
    # and also the new SUB buttons
    call_back_button_handler = CallbackQueryHandler(button)
    app.add_handler(call_back_button_handler)

    exec_message_handler = MessageHandler(
        exec_message_f,
        filters=filters.command([Command.EXEC]) & filters.user(users=Config.AUTH_USERS),
    )
    app.add_handler(exec_message_handler)

    eval_message_handler = MessageHandler(
        eval_message_f,
        filters=filters.command([Command.EVAL]) & filters.user(users=Config.AUTH_USERS),
    )
    app.add_handler(eval_message_handler)

    # MEMEs COMMANDs
    upload_document_handler = MessageHandler(
        upload_document_f,
        filters=filters.command([Command.UPLOAD])
        & filters.user(users=Config.AUTH_USERS),
    )
    app.add_handler(upload_document_handler)

    # HELP command
    help_text_handler = MessageHandler(
        help_message_f,
        filters=filters.command([Command.HELP]) & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(help_text_handler)

    # not AUTH CHANNEL users
    new_join_handler = MessageHandler(
        new_join_f, filters=~filters.chat(chats=Config.AUTH_CHATS)
    )
    app.add_handler(new_join_handler)

    # welcome MESSAGE
    group_new_join_handler = MessageHandler(
        help_message_f,
        filters=filters.chat(chats=Config.AUTH_CHATS) & filters.new_chat_members,
    )
    app.add_handler(group_new_join_handler)

    # savethumbnail COMMAND
    save_thumb_nail_handler = MessageHandler(
        save_thumb_nail,
        filters=filters.command([Command.SAVETHUMBNAIL])
        & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(save_thumb_nail_handler)

    # clearthumbnail COMMAND
    clear_thumb_nail_handler = MessageHandler(
        clear_thumb_nail,
        filters=filters.command([Command.CLEARTHUMBNAIL])
        & filters.chat(chats=Config.AUTH_CHATS),
    )
    app.add_handler(clear_thumb_nail_handler)

    # an probably easy way to get RClone CONF URI
    save_rclone_conf_handler = MessageHandler(
        save_rclone_conf_f,
        filters=filters.command([Command.GET_RCLONE_CONF_URI])
        & filters.user(users=Config.AUTH_USERS),
    )
    app.add_handler(save_rclone_conf_handler)

    # Telegram command to upload LOG files
    upload_log_f_handler = MessageHandler(
        upload_log_file,
        filters=filters.command([Command.UPLOAD_LOG_FILE])
        & filters.user(users=Config.AUTH_USERS),
    )
    app.add_handler(upload_log_f_handler)

    # run the APPlication
    app.run()
