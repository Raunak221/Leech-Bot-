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

import tempfile
from pathlib import Path, PurePath

import magic
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from publicleechgroup import LOGGER, Config
from publicleechgroup.helper_funcs.run_shell_command import run_command


async def split_large_files(input_file):
    file = Path(input_file)
    base_path = PurePath(file.resolve())
    # create a new download directory
    temp_dir = PurePath(tempfile.mkdtemp(dir=base_path.parent))

    file_type = magic.from_file(input_file, mime=True)
    if Config.SPLIT_ALGORITHM.lower() != "rar" and file_type.startswith("video/"):
        # handle video / audio files here
        metadata = extractMetadata(createParser(input_file))
        duration = metadata.get("duration").seconds if metadata.has("duration") else 0
        LOGGER(__name__).info(duration)

        # proprietary logic to get the seconds to trim (at)
        file_size = file.stat().st_size
        LOGGER(__name__).info(file_size)
        minimum_duration = (duration / file_size) * Config.MAX_SPLIT_SIZE
        # casting to int cuz float Time Stamp can cause errors
        minimum_duration = int(minimum_duration)
        LOGGER(__name__).info(minimum_duration)
        # END: proprietary

        start_time = 0
        end_time = minimum_duration

        i = 0
        flag = False

        while end_time <= duration:
            LOGGER(__name__).info(i)
            # file name generate
            parted_file_name = (
                f"{str(base_path.stem)}_PART_{str(i).zfill(2)}{str(base_path.suffix)}"
            )
            # [.stem] is for final path component without suffix
            # "Example.mp4" --> "Example_PART_00.mp4"

            output_path = temp_dir / parted_file_name
            cmd_split_video = [
                "ffmpeg",
                "-i",
                input_file,
                "-ss",
                str(start_time),
                "-to",
                str(end_time),
                "-async",
                "1",
                "-strict",
                "-2",
                "-c",
                "copy",
                output_path,
            ]
            LOGGER(__name__).info(cmd_split_video)
            await run_command(cmd_split_video)
            LOGGER(__name__).info(
                f"Start time {start_time}, End time {end_time}, Itr {i}"
            )

            # adding offset of 3 seconds to ensure smooth playback
            start_time = end_time - 3
            end_time += minimum_duration
            i += 1

            if (end_time > duration) and not flag:
                end_time = duration
                flag = True
            elif flag:
                break

    elif Config.SPLIT_ALGORITHM.lower() == "split":
        # handle normal files here
        output_path = temp_dir / f"{base_path.name}."
        cmd_create_split = [
            "split",
            "--numeric-suffixes=1",
            "--suffix-length=3",
            f"--bytes={Config.MAX_SPLIT_SIZE}",
            input_file,
            output_path,
        ]
        LOGGER(__name__).info(cmd_create_split)
        await run_command(cmd_create_split)
    elif Config.SPLIT_ALGORITHM.lower() == "rar":
        output_path = temp_dir / base_path.stem
        cmd_create_rar = [
            "rar",
            "a",
            f"-v{Config.MAX_SPLIT_SIZE}b",
            "-m0",
            output_path,
            input_file,
        ]
        LOGGER(__name__).info(cmd_create_rar)
        await run_command(cmd_create_rar)

    file.unlink()  # Remove input_file
    return temp_dir
