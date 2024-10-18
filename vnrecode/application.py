#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import shutil
import os

from .compress import Compress
from .printer import Printer
from .params import Params
from .utils import Utils


class Application:

    def __init__(self, params_inst: Params, compress_inst: Compress, printer_inst: Printer, utils_inst: Utils):
        self.__params = params_inst
        self.__compress = compress_inst.compress
        self.__printer = printer_inst
        self.__utils = utils_inst

    def run(self):
        start_time = datetime.now()
        self.__printer.win_ascii_esc()

        source = self.__params.source

        if self.__params.dest.exists():
            shutil.rmtree(self.__params.dest)

        self.__printer.info("Creating folders...")
        for folder, folders, files in os.walk(source):
            output = Path(folder.replace(str(source), str(self.__params.dest)))
            if not output.exists():
                os.mkdir(output)

            self.__printer.info(f'Compressing "{output}" folder...')

            with ThreadPoolExecutor(max_workers=self.__params.workers) as executor:
                futures = [
                    executor.submit(self.__compress, Path(folder, file), Path(output))
                    for file in files if Path(folder, file).is_file()
                ]
                for future in as_completed(futures):
                    future.result()

        self.__utils.print_duplicates()
        self.__utils.get_compression_status()
        self.__utils.sys_pause()
        print(f"Time taken: {datetime.now() - start_time}")