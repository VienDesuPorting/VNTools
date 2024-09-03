#!/usr/bin/env python3
from .application import Application
from .compress import Compress
from .printer import Printer
from .params import Params
from .utils import Utils


def init():
    params = Params.setup()
    printer = Printer(params.source)
    utils = Utils(params, printer)
    compress = Compress(params, printer, utils)

    Application(params, compress, printer, utils).run()


if __name__ == "__main__":
    init()