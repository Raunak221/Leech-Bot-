#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import shutil
from pathlib import Path, PurePath

from tobrot import LOGGER
from tobrot.helper_funcs.run_shell_command import run_command


async def create_archive(input_path):
    base_dir_name = PurePath(input_path).name[-249:]
    # nothing just 256 - 7 (.tar.gz), btw caption limit is 1024
    compressed_file_name = f"{base_dir_name}.tar.gz"
    # fix for https://t.me/c/1434259219/13344
    cmd_create_archive = [
        "tar",
        "-zcvf",
        compressed_file_name,
        f"{input_path}",
    ]
    LOGGER.info(cmd_create_archive)
    _, error = await run_command(cmd_create_archive)
    if error:
        LOGGER.info(error)
    # Wait for the subprocess to finish
    _path = Path(input_path)
    if _path.is_dir():
        shutil.rmtree(_path)
    elif _path.is_file():
        _path.unlink()
    return compressed_file_name if Path(compressed_file_name).exists() else None
