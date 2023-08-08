import os
from progress.bar import IncrementalBar


# Fill whole string with spaces for cleaning progress bar
def clean_str(string):
    return string + " " * (os.get_terminal_size().columns - len(string))


def info(string):
    print(clean_str(f"\r\033[0;32m[INFO]\033[0m {string}"))


def warning(string):
    print(clean_str(f"\r\033[0;33m[WARNING]\033[0m {string}"))


def error(string):
    print(clean_str(f"\r\033[0;31m[ERROR]\033[0m {string}"))


def bar_init(folder):
    file_count = 0
    for folder, folders, file in os.walk(folder):
        file_count += len(file)
    global bar
    bar = IncrementalBar('Compressing', max=file_count, suffix='[%(index)d/%(max)d] (%(percent).1f%%) - ETA: %(eta)ds')


def files(source, dest, dest_ext, comment):

    source_ext = os.path.splitext(source)[1]
    source_name = os.path.splitext(source)[0]

    print(clean_str(f"\r[COMP] \033[0;32m{source_name}\033[0m{source_ext}\033[0;32m -> {dest}\033[0m.{dest_ext}\033[0;32m ({comment})\033[0m"))
    bar.next()


def unknown_file(file):

    print(clean_str(f"\r[COMP] \033[0;33m{file}\033[0m"))
    bar.next()
