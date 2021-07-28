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
import os
import time
from pathlib import PurePath
from typing import List

import aiohttp
from PIL import Image


def humanbytes(size):
    # https://stackoverflow.com/a/43690506
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def time_formatter(seconds: int) -> str:
    result = ""
    remainder = seconds
    r_ange_s = {"days": (24 * 60 * 60), "hours": (60 * 60), "minutes": 60, "seconds": 1}
    for age, divisor in r_ange_s.items():
        v_m, remainder = divmod(remainder, divisor)
        v_m = int(v_m)
        if v_m != 0:
            result += f"{v_m} {age} "
    return result or "0 seconds"


async def fetch_thumbnail(image_url: str, output_dir: str) -> str:
    async with aiohttp.ClientSession() as session:
        noqa_read = await session.get(image_url)
        image_content = await noqa_read.read()
        thumb_img_path = os.path.join(output_dir, "thumb_image.jpg")
        with open(thumb_img_path, "wb") as f_d:
            f_d.write(image_content)
    # image might be downloaded in the previous step
    # https://stackoverflow.com/a/21669827/4723940
    Image.open(thumb_img_path).convert("RGB").save(thumb_img_path, "JPEG")
    # ref: https://t.me/PyrogramChat/44663
    # return the downloaded image path
    return thumb_img_path


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    output_file = PurePath(output_directory).joinpath(str(time.time()) + ".jpg")
    cmd_generate_thumbnail = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        output_file,
    ]
    # width = "90"
    await run_command(cmd_generate_thumbnail)
    # Wait for the subprocess to finish
    #
    return str(output_file)


async def run_command(shell_command: List) -> (str, str):
    """executes a shell_command,
    and returns the stdout and stderr"""
    process = await asyncio.create_subprocess_exec(
        *shell_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return t_response, e_response
