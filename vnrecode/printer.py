from time import sleep
import colorama
import sys
import os

from vnrecode.params import Params
from concurrent.futures import ThreadPoolExecutor


class Printer:
    """
    Class implements CLI UI for this utility
    """

    __anim = ["\u280b", "\u2819", "\u28e0", "\u28c4"]
    __ui_size = int
    __messages = []

    def __init__(self, params_inst: Params):
        """
        :param params_inst:
        """
        file_count = 0
        for folder, folders, file in os.walk(params_inst.source):
            file_count += len(file)
        self.workers = []
        self.__ui_size = 0
        self.__running = True
        self.__ui_updater = ThreadPoolExecutor().submit(self.update)

    def __print_msgs(self):
        for msg in self.__messages:
            self.__ui_size += 1
            print(msg)

    def __print_bar(self):
        from random import randint
        print(f"Recoding... [███████████████] {randint(0, 100)}%")
        self.__ui_size += 1

    def __print_folder(self):
        if len(self.workers) > 0:
            print(f"\x1b[2K\r\033[100m{self.workers[0]['path'][0].parent}\033[49m:")
            self.__ui_size += 1

    def __print_works(self, frame):
        for task in self.workers:
            if task['task'].__getstate__()['_state'] == "RUNNING":
                self.__ui_size += 1
                print(
                    f"[{self.__anim[frame % len(self.__anim)]}] "
                    f"\033[0;37m{task['path'][0].stem}\033[0m{task['path'][0].suffix}\033[0;37m -> "
                    f"{task['path'][0].stem}\033[0m.file")

    def __clear(self):
        print("\033[F\x1b[2K" * self.__ui_size, end='')
        self.__ui_size = 0

    def update(self):
        frame = 0
        while self.__running:
            self.__print_msgs()
            self.__print_bar()
            self.__print_folder()
            self.__print_works(frame)
            sleep(0.1)
            self.__clear()
            frame+=1

    def stop(self):
        self.__running = False
        self.__ui_updater.result()
        self.__print_msgs()

    def plain(self, string: str):
        self.__messages.append(string)

    def info(self, string: str):
        """
        Method prints string with decor for info messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"\x1b[2K\r\033[100m- {string}\033[49m")

    def warning(self, string: str):
        """
        Method prints string with decor for warning messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"\x1b[2K\r\033[93m!\033[0m {string}\033[49m")

    def error(self, string: str):
        """
        Method prints string with decor for error messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"\x1b[2K\r\033[31m\u2715\033[0m {string}\033[49m")

    @staticmethod
    def win_ascii_esc():
        """
        Method setups colorama for cmd
        :return: None
        """
        if sys.platform == "win32":
            colorama.init()