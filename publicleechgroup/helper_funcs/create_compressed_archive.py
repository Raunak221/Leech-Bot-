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

import shutil
from pathlib import Path, PurePath

from publicleechgroup import LOGGER
from publicleechgroup.helper_funcs.run_shell_command import run_command


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
    LOGGER(__name__).info(cmd_create_archive)
    _, error = await run_command(cmd_create_archive)
    if error:
        LOGGER(__name__).info(error)
    # Wait for the subprocess to finish
    _path = Path(input_path)
    if _path.is_dir():
        shutil.rmtree(_path)
    elif _path.is_file():
        _path.unlink()
    return compressed_file_name if Path(compressed_file_name).exists() else None
