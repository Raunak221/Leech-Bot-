#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

from pyrogram.types import CallbackQuery

from tobrot import LOGGER, String
from tobrot.helper_funcs.icntaosrtsba import leech_btn_k, ytdl_btn_k
from tobrot.helper_funcs.youtube_dl_button import youtube_dl_call_back


async def button(bot, update: CallbackQuery):
    LOGGER.info(update)
    if not update.message.reply_to_message:
        await update.answer(text=String.TGD_YTLD_STOOPID_DRUSER, show_alert=True)
        return

    if update.from_user.id != update.message.reply_to_message.from_user.id:
        return

    await update.answer()
    cb_data = update.data

    if cb_data.startswith("leech"):
        await leech_btn_k(update.message, cb_data)

    elif cb_data.startswith("ytdl"):
        await ytdl_btn_k(update.message)

    elif "|" in cb_data:
        await youtube_dl_call_back(bot, update)
