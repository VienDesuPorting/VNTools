#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import threading
import shutil
import os

from vnrecode.compress import Compress
from vnrecode.printer import Printer
from vnrecode.params import Params
from vnrecode.utils import Utils


class Application:
    """
    Main class for utility
    """

    semaphore: threading.Semaphore

    def __init__(self, params_inst: Params, compress_inst: Compress, printer_inst: Printer, utils_inst: Utils):
        self.__params = params_inst
        self.__compress = compress_inst.compress
        self.__printer = printer_inst
        self.__utils = utils_inst
        self.semaphore = threading.Semaphore(params_inst.workers)

    def worker(self, source: Path, output: Path):
        self.semaphore.acquire()
        free = self.__printer.active.index(None)
        self.__printer.active[free] = source

        self.__compress(source, output)
    
        self.semaphore.release()
        self.__printer.active[free] = None

    def run(self):
        """
        Method creates a folder in which all the recoded files will be placed,
        creates a queue of recoding processes for each file and, when the files are run out in the original folder,
        calls functions to display the result
        :return: None
        """
        start_time = datetime.now()
        self.__printer.win_ascii_esc()

        source = self.__params.source

        if self.__params.dest.exists():
            shutil.rmtree(self.__params.dest)

        ui_thread = threading.Thread(target=self.__printer.updater)
        ui_thread.start()

        threads = []
        for folder, folders, files in os.walk(source):
            output = self.__utils.get_comp_subdir(folder)
            if not output.exists():
                os.mkdir(output)

            for file in files: 
                if Path(folder, file).is_file():
                    th = threading.Thread(target=self.worker, args=(Path(folder, file), Path(output)))
                    threads.append(th)
                    th.start()

        for thread in threads:
            thread.join()

        self.__printer.stop_event.set()
        ui_thread.join()
        self.__utils.print_duplicates()
        self.__utils.get_recode_status()
        self.__utils.sys_pause()
        print(f"Time taken: {datetime.now() - start_time}")