#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import time
from pathlib import Path, PurePath

from tobrot.helper_funcs.run_shell_command import run_command


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
    return str(output_file) if Path(output_file).exists() else None
