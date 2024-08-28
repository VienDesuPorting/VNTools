#!/usr/bin/env python3
from .application import Application
from .compress import Compress
from .printer import Printer
from .config import Config
from .utils import Utils


def init():
    config = Config.setup_config()
    printer = Printer(config.args.source)
    utils = Utils(config.config, printer)
    compress = Compress(config.config, printer, utils)

    Application(config, compress, printer, utils).run()


if __name__ == "__main__":
    init()