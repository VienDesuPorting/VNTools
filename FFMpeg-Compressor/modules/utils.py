from modules import printer
import os


def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def get_compression(orig, comp):
    comp = 100 - int((get_dir_size(comp) / get_dir_size(orig)) * 100)
    if comp < 0:
        printer.warning(f'Compression: {comp}%')
        printer.warning("The resulting files are larger than the original ones!")
    else:
        printer.info(f'Compression: {comp}%')
