from progress.bar import IncrementalBar
import colorama
import sys
import os


def bar_init(folder):
    file_count = 0
    for folder, folders, file in os.walk(folder):
        file_count += len(file)
    global bar
    bar = IncrementalBar('Compressing', max=file_count, suffix='[%(index)d/%(max)d] (%(percent).1f%%)')
    bar.update()


def bar_print(string):
    print(string)
    bar.update()


# Fill whole string with spaces for cleaning progress bar
def clean_str(string):
    return string + " " * (os.get_terminal_size().columns - len(string))


def info(string):
    bar_print(clean_str(f"\r\033[100m- {string}\033[49m"))


def warning(string):
    bar_print(clean_str(f"\r\033[93m!\033[0m {string}\033[49m"))


def error(string):
    bar_print(clean_str(f"\r\033[31m\u2715\033[0m {string}\033[49m"))


def files(source, dest, dest_ext, comment):
    source_ext = os.path.splitext(source)[1]
    source_name = os.path.splitext(source)[0]

    bar_print(clean_str(f"\r\033[0;32m\u2713\033[0m \033[0;37m{source_name}\033[0m{source_ext}\033[0;37m -> {dest}\033[0m.{dest_ext}\033[0;37m ({comment})\033[0m"))


def unknown_file(file):
    bar_print(clean_str(f"\r* \033[0;33m{file}\033[0m (File will be force compressed via ffmpeg)"))


def win_ascii_esc():
    if sys.platform == "win32":
        colorama.init()
