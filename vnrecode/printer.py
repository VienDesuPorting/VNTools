from progress.bar import IncrementalBar
from pathlib import Path
import colorama
import sys
import os

class Printer:

    def __init__(self, folder: Path):
        file_count = 0
        for folder, folders, file in os.walk(folder):
            file_count += len(file)
        self.bar = IncrementalBar('Compressing', max=file_count, suffix='[%(index)d/%(max)d] (%(percent).1f%%)')
        self.bar.update()

    # Fill whole string with spaces for cleaning progress bar
    @staticmethod
    def clean_str(string: str) -> str:
        return string + " " * (os.get_terminal_size().columns - len(string))

    @staticmethod
    def win_ascii_esc():
        if sys.platform == "win32":
            colorama.init()

    def bar_print(self, string: str):
        print(string)
        self.bar.update()

    def info(self, string: str):
        self.bar_print(self.clean_str(f"\r\033[100m- {string}\033[49m"))

    def warning(self, string: str):
        self.bar_print(self.clean_str(f"\r\033[93m!\033[0m {string}\033[49m"))

    def error(self, string: str):
        self.bar_print(self.clean_str(f"\r\033[31m\u2715\033[0m {string}\033[49m"))

    def files(self, source_path: Path, output_path: Path, comment: str):
        self.bar_print(self.clean_str(f"\r\033[0;32m\u2713\033[0m \033[0;37m{source_path.stem}\033[0m{source_path.suffix}\033[0;37m -> "
                                      f"{source_path.stem}\033[0m{output_path.suffix}\033[0;37m ({comment})\033[0m"))

    def unknown_file(self, file: str):
        self.bar_print(self.clean_str(f"\r* \033[0;33m{file}\033[0m (File will be force compressed via ffmpeg)"))
