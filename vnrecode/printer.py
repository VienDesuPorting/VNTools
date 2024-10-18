from progress.bar import IncrementalBar
from pathlib import Path
import colorama
import sys
import os
import re

class Printer:
    """
    Class implements CLI UI for this utility
    """

    def __init__(self, source: Path):
        """
        :param source: Path of original (compressing) folder to count its files for progress bar
        """
        file_count = 0
        for folder, folders, file in os.walk(source):
            file_count += len(file)
        self.bar = IncrementalBar('Compressing', max=file_count, suffix='[%(index)d/%(max)d] (%(percent).1f%%)')
        self.bar.update()

    @staticmethod
    def clean_str(string: str) -> str:
        """
        Method fills end of string with spaces to remove progress bar garbage from console
        :param string: String to "clean"
        :return: "Clean" string
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return string + " " * (os.get_terminal_size().columns - len(ansi_escape.sub('', string)))

    @staticmethod
    def win_ascii_esc():
        """
        Method setups colorama for cmd
        :return: None
        """
        if sys.platform == "win32":
            colorama.init()

    def bar_print(self, string: str):
        """
        Method prints some string in console and updates progress bar
        :param string: String to print
        :return: None
        """
        print(string)
        self.bar.update()

    def info(self, string: str):
        """
        Method prints string with decor for info messages
        :param string: String to print
        :return: None
        """
        self.bar_print(self.clean_str(f"\r\033[100m- {string}\033[49m"))

    def warning(self, string: str):
        """
        Method prints string with decor for warning messages
        :param string: String to print
        :return: None
        """
        self.bar_print(self.clean_str(f"\r\033[93m!\033[0m {string}\033[49m"))

    def error(self, string: str):
        """
        Method prints string with decor for error messages
        :param string: String to print
        :return: None
        """
        self.bar_print(self.clean_str(f"\r\033[31m\u2715\033[0m {string}\033[49m"))

    def files(self, source_path: Path, output_path: Path, comment: str):
        """
        Method prints the result of recoding a file with some decorations in the form:
        input file name -> output file name (quality setting)
        :param source_path: Input file Path
        :param output_path: Output file Path
        :param comment: Comment about recode quality setting
        :return: None
        """
        self.bar_print(self.clean_str(f"\r\033[0;32m\u2713\033[0m \033[0;37m{source_path.stem}\033[0m{source_path.suffix}\033[0;37m -> "
                                      f"{source_path.stem}\033[0m{output_path.suffix}\033[0;37m ({comment})\033[0m"))

    def unknown_file(self, filename: str):
        """
        Method prints the result of recoding unknown file
        :param filename: Name of unknown file
        :return:
        """
        self.bar_print(self.clean_str(f"\r\u2713 \033[0;33m{filename}\033[0m (File will be force compressed via ffmpeg)"))
