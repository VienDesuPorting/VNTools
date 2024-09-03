#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import shutil
import os


class Application:

    def __init__(self, params, compress, printer, utils):
        self.params = params
        self.compress = compress.compress
        self.printer = printer
        self.utils = utils

    def compress_worker(self, folder, file, source, output):
        if os.path.isfile(f'{folder}/{file}'):
            self.compress(folder, file, source, output)

    def run(self):
        start_time = datetime.now()
        self.printer.win_ascii_esc()

        source = os.path.abspath(self.params.source)

        if os.path.exists(f"{source}_compressed"):
            shutil.rmtree(f"{source}_compressed")

        self.printer.info("Creating folders...")
        for folder, folders, files in os.walk(source):
            if not os.path.exists(folder.replace(source, f"{source}_compressed")):
                os.mkdir(folder.replace(source, f"{source}_compressed"))

            self.printer.info(f'Compressing "{folder.replace(source, os.path.split(source)[-1])}" folder...')
            output = folder.replace(source, f"{source}_compressed")

            with ThreadPoolExecutor(max_workers=self.params.workers) as executor:
                futures = [
                    executor.submit(self.compress, folder, file, source, output)
                    for file in files if os.path.isfile(f'{folder}/{file}')
                ]
                for future in as_completed(futures):
                    future.result()

        self.utils.print_duplicates()
        self.utils.get_compression_status(source)
        self.utils.sys_pause()
        print(f"Time taken: {datetime.now() - start_time}")