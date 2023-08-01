from modules import printer
import os


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
        comp = 100 - int((get_dir_size(comp, processed_files) / get_dir_size(orig, processed_files)) * 100)
        if comp < 0:
            printer.warning(f'Compression: {comp}%')
            printer.warning("The resulting files are larger than the original ones!")
        else:
            printer.info(f'Compression: {comp}%')
    except ZeroDivisionError:
        printer.warning("Nothing compressed!")


def get_compression_status(orig_folder):
    orig_folder_len = 0
    comp_folder_len = 0

    for folder, folders, file in os.walk(orig_folder):
        orig_folder_len += len(file)

    for folder, folders, file in os.walk(f'{orig_folder}_compressed'):
        comp_folder_len += len(file)

    if orig_folder_len == comp_folder_len:
        printer.info("Success!")
        get_compression(orig_folder, f"{orig_folder}_compressed")
    else:
        printer.warning("Some files failed to compress!")
        get_compression(orig_folder, f"{orig_folder}_compressed")


def help_message():
    text = "Usage: main.py {folder}"
    return text
