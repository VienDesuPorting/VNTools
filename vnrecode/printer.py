import sys
import colorama
from time import sleep
from threading import Event

from vnrecode.params import Params

CLR = "\033[K\r"
RET = "\033[F"
# CLR = "CLR"
# RET = "RET"

class Printer:
    """
    Class implements CLI UI for this utility
    """

    __messages = []
    cursor = ['|', '/', '-', '\\']
    active = []
    threads_n: int
    stop_event: Event
    update_rate = 0.25

    def __init__(self, params: Params):
        self.threads_n = params.workers
        self.active = [None]*params.workers
        self.stop_event = Event()

    @staticmethod
    def win_ascii_esc():
        """
        Method setups colorama for cmd
        :return: None
        """
        if sys.platform == "win32":
            colorama.init()

    def print(self, string: str):
        """
        Method prints some string in console in ui thread
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"{string}")

    def info(self, string: str):
        """
        Method prints string with decor for info messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"[I] {string}")

    def warning(self, string: str):
        """
        Method prints string with decor for warning messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"[W] {string}")

    def error(self, string: str):
        """
        Method prints string with decor for error messages
        :param string: String to print
        :return: None
        """
        self.__messages.append(f"[E] {string}")

    def __print_messages(self):
        for msg in self.__messages:
            print(f"{CLR}{msg}")
            self.__messages.remove(msg)

    def updater(self):
        cursor_frame = 0
        while True:
            if self.stop_event.is_set():
                break
            self.__print_messages()
            for file in self.active:
                if file:
                    print(CLR, '*', file)
                else:
                    print(CLR, '*', "IDLE")
            print(f"{CLR}Progress: 10/30 (33%)", self.cursor[cursor_frame])
            cursor_frame += 1
            if cursor_frame > len(self.cursor)-1: cursor_frame = 0

            sleep(self.update_rate)
            print(RET * (self.threads_n+1), end="") # Move cursor up
