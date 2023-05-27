#!/bin/python3

from modules import compressor
from modules import printer
from modules import utils
import os

orig_folder = input("Folder: ").replace("'", "")

try:
    os.mkdir(f"{orig_folder}_compressed")
    printer.info(f"Created {orig_folder}_compressed folder")
except OSError:
    pass

printer.info("Compression started!")
compressor.compress(orig_folder)

if len(os.listdir(path=orig_folder)) == len((os.listdir(path=f"{orig_folder}_compressed"))):
    printer.info("Success!")
    utils.get_compression(orig_folder, f"{orig_folder}_compressed")
else:
    printer.warning("Some files failed to compress!")
    utils.get_compression(orig_folder, f"{orig_folder}_compressed")
