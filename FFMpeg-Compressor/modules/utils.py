from modules import configloader
from modules import printer
from shutil import copyfile
from glob import glob
import os

errors_count = 0


def get_dir_size(directory, files):
    total_size = 0
    for folder, folders, files in os.walk(directory):
        for file in files:
            if not os.path.islink(f"{folder}/{file}"):
                total_size += os.path.getsize(f"{folder}/{file}")
    return total_size


def get_compression(orig, comp):
    processed_files = []
    for folder, folders, files in os.walk(comp):
        for file in files:
            processed_files.append(file)
    try:
        orig = get_dir_size(orig, processed_files)
        comp = get_dir_size(comp, processed_files)

        print(f"Result: {orig/1024/1024:.2f}MB -> {comp/1024/1024:.2f}MB Δ {(orig - comp)/1024/1024:.2f}MB")
    except ZeroDivisionError:
        printer.warning("Nothing compressed!")


def get_compression_status(orig_folder):
    orig_folder_len = 0
    comp_folder_len = 0

    for folder, folders, files in os.walk(orig_folder):
        orig_folder_len += len(files)

    for folder, folders, files in os.walk(f'{orig_folder}_compressed'):
        for file in files:
            if not os.path.splitext(file)[1].count(" (copy)"):
                comp_folder_len += 1

    if errors_count != 0:
        printer.warning("Some files failed to compress!")

    if orig_folder_len == comp_folder_len:
        printer.info("Success!")
        get_compression(orig_folder, f"{orig_folder}_compressed")
    else:
        printer.warning("Original and compressed folders are not identical!")
        get_compression(orig_folder, f"{orig_folder}_compressed")


def add_unprocessed_file(orig_folder, new_folder):
    if configloader.config['FFMPEG']['CopyUnprocessed']:
        filename = orig_folder.split().pop()
        copyfile(orig_folder, new_folder)
        printer.info(f"File {filename} copied to compressed folder.")


def check_duplicates(new_folder):
    filename = new_folder.split().pop()
    if os.path.exists(new_folder):
        printer.warning(
            f'Duplicate file has been found! Check manually this files - "{filename}", '
            f'"{os.path.splitext(filename)[0] + "(copy)" + os.path.splitext(filename)[1]}"')
        return os.path.splitext(new_folder)[0] + "(copy)" + os.path.splitext(new_folder)[1]
    return new_folder


def help_message():
    return "Usage: ffmpeg-comp {folder}"
