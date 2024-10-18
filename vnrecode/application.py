#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import shutil
import os

from .compress import Compress
from .printer import Printer
from .params import Params
from .utils import Utils


class Application:

    def __init__(self, params: Params, compress: Compress, printer: Printer, utils: Utils):
        self.__params = params
        self.__compress = compress.compress
        self.__printer = printer
        self.__utils = utils

    def run(self):
        start_time = datetime.now()
        self.__printer.win_ascii_esc()

        source = self.__params.source

        if os.path.exists(self.__params.dest):
            shutil.rmtree(self.__params.dest)

        self.__printer.info("Creating folders...")
        for folder, folders, files in os.walk(source):
            if not os.path.exists(folder.replace(source, self.__params.dest)):
                os.mkdir(folder.replace(source, self.__params.dest))

            self.__printer.info(f'Compressing "{folder.replace(source, os.path.split(source)[-1])}" folder...')
            output = folder.replace(source, self.__params.dest)

            with ThreadPoolExecutor(max_workers=self.__params.workers) as executor:
                futures = [
                    executor.submit(self.__compress, folder, file, output)
                    for file in files if os.path.isfile(os.path.join(folder, file))
                ]
                for future in as_completed(futures):
                    future.result()

        self.__utils.print_duplicates()
        self.__utils.get_compression_status()
        self.__utils.sys_pause()
        print(f"Time taken: {datetime.now() - start_time}")