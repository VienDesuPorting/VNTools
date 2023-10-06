#!python3

from modules import configloader
from modules import compressor
from modules import printer
from modules import utils
import shutil
import sys
import os

try:
    if sys.argv[1][len(sys.argv[1])-1] == "/":
        arg_path = sys.argv[1][:len(sys.argv[1])-1]
    else:
        arg_path = sys.argv[1]
except IndexError:
    print(utils.help_message())
    exit()

orig_folder = arg_path
printer.orig_folder = arg_path

printer.bar_init(orig_folder)

if os.path.exists(f"{orig_folder}_compressed"):
    shutil.rmtree(f"{orig_folder}_compressed")

printer.info("Creating folders...")
for folder, folders, files in os.walk(orig_folder):
    if not os.path.exists(folder.replace(orig_folder, f"{orig_folder}_compressed")):
        os.mkdir(folder.replace(orig_folder, f"{orig_folder}_compressed"))

    printer.info(f"Compressing \"{folder.replace(orig_folder, orig_folder.split('/').pop())}\" folder...")
    target_folder = folder.replace(orig_folder, f"{orig_folder}_compressed")
    for file in os.listdir(folder):
        if os.path.isfile(f'{folder}/{file}'):
            match compressor.get_file_type(file):
                case "audio":
                    comp_file = compressor.compress_audio(folder, file, target_folder)
                case "image":
                    comp_file = compressor.compress_image(folder, file, target_folder)
                case "video":
                    comp_file = compressor.compress_video(folder, file, target_folder)
                case "unknown":
                    comp_file = compressor.compress(folder, file, target_folder)

            utils.check_file_existing(folder.replace(orig_folder, f"{orig_folder}_compressed"), file)

            if configloader.config['FFMPEG']['MimicMode']:
                try:
                    os.rename(comp_file, f'{folder}/{file}'.replace(orig_folder, f"{orig_folder}_compressed"))
                except FileNotFoundError:
                    printer.error(f"File {file} can't be processed! Maybe it is ffmpeg error or unsupported file. "
                                  f"You can change -loglevel in ffmpeg parameters to see full error.")

if configloader.config['FFMPEG']['CopyUnprocessed']:
    printer.info("Copying unprocessed files...")
    utils.add_unprocessed_files(orig_folder)
utils.get_compression_status(orig_folder)
