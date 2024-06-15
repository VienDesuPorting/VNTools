#!/usr/bin/env python3

from modules import compressor
from modules import printer
from modules import utils
from datetime import datetime
import shutil
import sys
import os


def get_args():
    try:
        if sys.argv[1][len(sys.argv[1])-1] == "/":
            path = sys.argv[1][:len(sys.argv[1])-1]
        else:
            path = sys.argv[1]
        return path
    except IndexError:
        print(utils.help_message())
        exit()


if __name__ == "__main__":
    start_time = datetime.now()
    printer.win_ascii_esc()
    req_folder = os.path.abspath(get_args())

    printer.bar_init(req_folder)

    if os.path.exists(f"{req_folder}_compressed"):
        shutil.rmtree(f"{req_folder}_compressed")

    printer.info("Creating folders...")
    for folder, folders, files in os.walk(req_folder):
        if not os.path.exists(folder.replace(req_folder, f"{req_folder}_compressed")):
            os.mkdir(folder.replace(req_folder, f"{req_folder}_compressed"))

        printer.info(f"Compressing \"{folder.replace(req_folder, req_folder.split('/').pop())}\" folder...")
        target_folder = folder.replace(req_folder, f"{req_folder}_compressed")
        for file in files:
            if os.path.isfile(f'{folder}/{file}'):
                compressor.compress_file(folder, file, target_folder, req_folder)

    utils.get_compression_status(req_folder)
    utils.sys_pause()
    print(f"Time taken: {datetime.now() - start_time}")
