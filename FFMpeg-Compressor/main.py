#!python3

from modules import configloader
from modules import compressor
from modules import printer
from modules import utils
from datetime import datetime
import multiprocessing
import shutil
import sys
import os


def get_file_type(filename):
    audio_ext = ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma']
    image_ext = ['.apng', '.avif', '.bmp', '.tga', '.tiff', '.dds', '.svg', '.webp', '.jpg', '.jpeg', '.png']
    video_ext = ['.3gp' '.amv', '.avi', '.gif', '.m2t', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv',
                 '.webm', '.ogv']

    if os.path.splitext(filename)[1] in audio_ext:
        return "audio"
    elif os.path.splitext(filename)[1] in image_ext:
        return "image"
    elif os.path.splitext(filename)[1] in video_ext:
        return "video"
    else:
        return "unknown"


def process_file(folder_name, file_name, target_folder_name, orig_folder_name):
    if os.path.isfile(f'{folder_name}/{file_name}'):
        match get_file_type(file_name):
            case "audio":
                comp_file = compressor.compress_audio(folder_name, file_name, target_folder_name,
                                                      configloader.config['AUDIO']['Extension'])
            case "image":
                comp_file = compressor.compress_image(folder_name, file_name, target_folder_name,
                                                      configloader.config['IMAGE']['Extension'])
            case "video":
                comp_file = compressor.compress_video(folder_name, file_name, target_folder_name,
                                                      configloader.config['VIDEO']['Extension'])
            case "unknown":
                comp_file = compressor.compress(folder_name, file_name, target_folder_name)

        if configloader.config['FFMPEG']['MimicMode']:
            try:
                os.rename(comp_file, f'{folder_name}/{file_name}'.replace(orig_folder_name, f"{orig_folder_name}_compressed"))
            except FileNotFoundError:
                pass


if __name__ == "__main__":
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
    start_time = datetime.now()
    for folder, folders, files in os.walk(orig_folder):
        if not os.path.exists(folder.replace(orig_folder, f"{orig_folder}_compressed")):
            os.mkdir(folder.replace(orig_folder, f"{orig_folder}_compressed"))

        printer.info(f"Compressing \"{folder.replace(orig_folder, orig_folder.split('/').pop())}\" folder...")
        target_folder = folder.replace(orig_folder, f"{orig_folder}_compressed")
        with multiprocessing.Pool(processes=configloader.config['FFMPEG']['Threads']) as pool:
            processes = []
            for file in os.listdir(folder):
                processes.append(pool.apply_async(process_file, args=(folder, file, target_folder, orig_folder)))
            for proc in processes:
                proc.get()

    if configloader.config['FFMPEG']['CopyUnprocessed']:
        printer.info("Copying unprocessed files...")
        utils.add_unprocessed_files(orig_folder)
    print(f"Compression time = {datetime.now() - start_time}")
    utils.get_compression_status(orig_folder)
