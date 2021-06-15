#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


from tobrot import String


async def new_join_f(client, message):
    # delete all other messages, except for AUTH_CHANNEL
    await message.delete(revoke=True)
    # reply the correct CHAT ID,
    # and LEAVE the chat
    chat_type = message.chat.type
    if chat_type != "private":
        await message.reply_text(String.WRONG_MESSAGE.format(CHAT_ID=message.chat.id))
        # leave chat
        await message.chat.leave()


async def help_message_f(client, message):
    # display the /help message
    await message.reply_text(String.HELP_MESSAGE, quote=True)
