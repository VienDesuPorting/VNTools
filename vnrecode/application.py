#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import shutil
import psutil
import signal
import os

from vnrecode.compress import Compress
from vnrecode.printer import Printer
from vnrecode.params import Params
from vnrecode.utils import Utils

class Application:
    """
    Main class for utility
    """

    def __init__(self, params_inst: Params, compress_inst: Compress, printer_inst: Printer, utils_inst: Utils):
        self.__params = params_inst
        self.__compress = compress_inst.compress
        self.__printer = printer_inst
        self.__utils = utils_inst

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

        for folder, folders, files in os.walk(source):
            output = self.__utils.get_comp_subdir(folder)
            if not output.exists():
                os.mkdir(output)

            for chunk in range(0, len(files), self.__params.workers):
                with ThreadPoolExecutor(max_workers=self.__params.workers) as executor:
                    self.__printer.workers = []
                    #for file in files:
                    for file in files[chunk:chunk+self.__params.workers]:
                        if Path(folder, file).is_file():
                            work_dict = {
                                "task": executor.submit(self.__compress, Path(folder, file), Path(output)),
                                "path": [Path(folder, file), Path(output)]
                            }
                            self.__printer.workers.append(work_dict)

        self.__utils.print_duplicates()
        self.__utils.get_recode_status()
        self.__printer.plain(f"Time taken: {datetime.now() - start_time}")
        self.__printer.stop()
        self.__utils.sys_pause()