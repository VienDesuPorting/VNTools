#!/usr/bin/env python3
from .application import Application
from .compress import Compress
from .printer import Printer
from .params import Params
from .config import Config
from .utils import Utils


def init():
    config = Config.setup_config()
    params = Params.setup(config.config, config.args)
    printer = Printer(config.args.source)
    utils = Utils(params, printer)
    compress = Compress(params, printer, utils)

    Application(params, config.args, compress, printer, utils).run()


if __name__ == "__main__":
    init()