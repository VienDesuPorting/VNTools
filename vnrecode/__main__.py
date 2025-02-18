#!/usr/bin/env python3
from vnrecode.application import Application
from vnrecode.compress import Compress
from vnrecode.printer import Printer
from vnrecode.params import Params
from vnrecode.utils import Utils


def init():
    """
    This function creates all needed class instances and run utility
    :return: None
    """
    params = Params.setup()
    printer = Printer(params.source)
    utils = Utils(params, printer)
    compress = Compress(params, printer, utils)

    Application(params, compress, printer, utils).run()


if __name__ == "__main__":
    init()