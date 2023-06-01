from modules import printer
import glob
import os


def get_dir_size(directory, files):
    total_size = 0
    for f in files:
        fp = glob.glob(f'{directory}/{f}*')[0]
        if not os.path.islink(fp):
            total_size += os.path.getsize(fp)
    return total_size


def get_compression(orig, comp):
    processed_files = []
    for file in os.listdir(comp):
        processed_files.append(os.path.splitext(file)[0])

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

    for file in os.listdir(orig_folder):
        if os.path.isfile(f'{orig_folder}/{file}'):
            orig_folder_len += 1

    for file in os.listdir(orig_folder):
        if os.path.isfile(f'{orig_folder}_compressed/{file}'):
            comp_folder_len += 1

    if orig_folder_len == comp_folder_len:
        printer.info("Success!")
        get_compression(orig_folder, f"{orig_folder}_compressed")
    else:
        printer.warning("Some files failed to compress!")
        get_compression(orig_folder, f"{orig_folder}_compressed")


def help_message():
    text = "Usage: main.py {folder}"
    return text
