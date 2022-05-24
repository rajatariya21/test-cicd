"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import io
import os
import pathlib
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping
from typing.io import TextIO
import json

import pandas as pd
from airbyte_protocol import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
)
from airbyte_protocol.models import DestinationSyncMode, Type
from base_python import AirbyteLogger, Destination


class DestinationLocal(Destination):
    def _create_directory_if_not_exists(self, directory: str):
        Path(directory).mkdir(parents=True, exist_ok=True)

    def _get_mounted_directory(self, output_dir):
        return os.path.join("/local", output_dir)

    def check(
        self, logger: AirbyteLogger, config: Mapping[str, any]
    ) -> AirbyteConnectionStatus:
        """
        Verify if the provided configuration can be used to run a sync.
        To do this we just verify if we can create the output destination. A failure will mean something like e.g: not having permissions.
        """
        output_directory = self._get_mounted_directory(config["output_directory"])
        try:
            self._create_directory_if_not_exists(output_directory)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            msg = f"Cannot create output directory at {output_directory}. The following error occurred: {e}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=msg)

    def _sync_mode_to_open_mode(self, mode: DestinationSyncMode):
        if mode == DestinationSyncMode.overwrite:
            return "w"
        elif mode == DestinationSyncMode.append:
            return "a"
        else:
            raise Exception(f"Unuspported sync mode: {mode}")

    def read_record_messages(
        self, stdin: io.TextIOWrapper
    ) -> Iterable[AirbyteRecordMessage]:
        for line in stdin:
            try:
                msg = AirbyteMessage.parse_raw(line)
                if msg.type == Type.RECORD:
                    yield msg.record
            except Exception:
                self.logger.info(f"ignoring non-record input: {line}")
        yield from []

    def write(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, any],
        configured_catalog: ConfiguredAirbyteCatalog,
    ):
        stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        # logger.info("***************************")
        # logger.info(str(stdin))
        # logger.info(str(list(stdin)))
        # logger.info("***************************")
        output_directory = self._get_mounted_directory(config["output_directory"])
        stream = []
        data = []
        emitted_at = []
        file_name = "default"
        for record_message in self.read_record_messages(stdin):
            stream.append(record_message.stream)
            data.append(json.dumps(record_message.data))
            emitted_at.append(record_message.emitted_at)
            # logger.info("***************************")
            # logger.info(output_directory)
            # logger.info(pathlib.PosixPath(output_directory).is_dir())
            # logger.info(str(pathlib.PosixPath(".").absolute().as_posix()))
            # logger.info("HERE record_message")
            # logger.info(str(record_message))
            # logger.info(str(type(record_message)))
            # logger.info(str(dir(record_message)))
            # logger.info("HERE record_message.stream")
            # logger.info(record_message.stream)
            # logger.info("HERE record_message.data")
            # logger.info(str(record_message.data))
        df = pd.DataFrame()
        df["stream"] = stream
        df["data"] = data
        df["emitted_at"] = emitted_at
        # my_dict = defaultdict(list)
        # for record_message in self.read_record_messages(stdin):
        #     for k, v in record_message.data.items():
        #         my_dict[k].append(v)
        # my_dict = dict(my_dict)
        # df = pd.DataFrame(my_dict)
        # logger.info("***************************")
        # logger.info(str(my_dict))
        # logger.info("***************************")
        output_path = pathlib.PosixPath(output_directory)
        output_path = output_path / "{}.csv".format(file_name)
        df.to_csv(output_path.as_posix())
