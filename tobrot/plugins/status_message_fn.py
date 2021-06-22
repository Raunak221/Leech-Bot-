#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import asyncio
import io
import os
import shutil
import sys
import time
import traceback

from tobrot import BOT_START_TIME, LOGGER, Command, Config, String, aria2
from tobrot.helper_funcs.display_progress import humanbytes, time_formatter
from tobrot.helper_funcs.upload_to_tg import upload_to_tg


async def status_message_f(_, message):
    # Show All Downloads
    downloads = aria2.get_downloads()
    #
    DOWNLOAD_ICON = "📥"
    UPLOAD_ICON = "📤"
    #
    msg = ""
    for download in downloads:
        msg += (
            f"<u>{download.name}</u> | "
            f"{download.total_length_string()} | "
            f"{download.progress_string()} | "
            f"{DOWNLOAD_ICON} {download.download_speed_string()} | "
            f"{UPLOAD_ICON} {download.upload_speed_string()} | "
            f"{download.eta_string()} | "
            f"{download.status}"
        )
        if not download.is_complete:
            msg += f"\n<code>/{Command.CANCEL} {download.gid}</code>"
        msg += "\n\n"
    # LOGGER.info(msg)

    if msg == "":
        msg = String.NO_TOR_STATUS

    currentTime = time_formatter((time.time() - BOT_START_TIME))
    total, used, free = shutil.disk_usage(".")

    ms_g = (
        f"<b>Bot Uptime</b>: <code>{currentTime}</code>\n"
        f"<b>Total disk space</b>: <code>{humanbytes(total)}</code>\n"
        f"<b>Used</b>: <code>{humanbytes(used)}</code>\t"
        f"<b>Free</b>: <code>{humanbytes(free)}</code>\n"
    )

    msg = ms_g + "\n" + msg
    await message.reply_text(msg, quote=True)


async def cancel_message_f(_, message):
    if len(message.command) > 1:
        # /cancel command
        i_m_s_e_g = await message.reply_text(String.PROCESSING, quote=True)
        g_id = message.command[1].strip()
        LOGGER.info(g_id)
        try:
            downloads = aria2.get_download(g_id)
            LOGGER.info(downloads)
            LOGGER.info(downloads.remove(force=True, files=True))
            await i_m_s_e_g.edit_text(String.TOR_CANCELLED)
        except Exception as e:
            LOGGER.warn(str(e))
            await i_m_s_e_g.edit_text(String.TOR_CANCEL_FAILED)
    else:
        await message.delete()


async def exec_message_f(_, message):
    # DELAY_BETWEEN_EDITS = 0.3
    # PROCESS_RUN_TIME = 100
    _text = await message.reply_text("...")
    cmd = message.text.split(" ", maxsplit=1)[1]

    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    # start_time = time.time() + PROCESS_RUN_TIME
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "None"
    o = stdout.decode()
    if not o:
        o = "None"
    OUTPUT = ""
    OUTPUT += (
        "<b>EXEC:</b>\n"
        f"<u>Command:</u> <code>{cmd}</code>\n"
        f"<u>PID</u>: <code>{process.pid}</code>\n"
        f"<b>stderr:</b>\n<code>{e}</code>\n"
        f"<b>stdout:</b>\n<code>{o}</code>\n"
        f"<b>return:</b> <code>{process.returncode}</code>"
    )

    if len(OUTPUT) > Config.MAX_MESSAGE_LENGTH:
        with open("exec.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(OUTPUT))
        await message.reply_document(
            document="exec.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id,
        )
        os.remove("exec.text")
        await _text.delete()
    else:
        await _text.edit_text(OUTPUT)


async def upload_document_f(_, message):
    imsegd = await message.reply_text(String.PROCESSING)
    if " " in message.text:
        recvd_command, local_file_name = message.text.split(" ", 1)
        recvd_response = await upload_to_tg(
            imsegd, local_file_name, message.from_user.id, {}
        )
        LOGGER.info(recvd_response)
    await imsegd.delete()


async def upload_log_file(_, message):
    await message.reply_document("PublicLeech.log")


async def eval_message_f(client, message):
    _text = await message.reply_text("...")
    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_id = message.message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    # evaluation = ""
    if exc:
        evaluation = exc.strip()
    elif stderr:
        evaluation = stderr.strip()
    elif stdout:
        evaluation = stdout.strip()
    else:
        evaluation = "None"

    final_output = ""
    final_output += f"<b>EVAL</b>: <code>{cmd}</code>"
    final_output += "\n\n<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation}</code>\n"

    if len(final_output) > Config.MAX_MESSAGE_LENGTH:
        with open("eval.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(final_output))
        await message.reply_document(
            document="eval.text",
            caption=cmd,
            disable_notification=True,
            reply_to_message_id=reply_to_id,
        )
        os.remove("eval.text")
        await _text.delete()
    else:
        await _text.edit_text(final_output)


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)
