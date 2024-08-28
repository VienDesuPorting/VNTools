#!/usr/bin/env python3
import colorama
import argparse
import sys
import os

from .printer import Printer
from .actions import Actions


def args_init():
    parser = argparse.ArgumentParser(
        prog='unrenapk',
        description='Extract Ren\'Py .apk and .obb files into Ren\'Py SDK\'s project'
    )
    parser.add_argument('path')
    parser.add_argument('-o', '--output')
    return parser.parse_args()

def launch():
    if sys.platform == "win32":
        colorama.init()
    args = args_init()
    if args.output:
        output = args.output
    else:
        output = ''
    actions = Actions(output)
    printer = Printer()

    filename = args.path
    if os.path.splitext(filename)[1] == '.apk' or os.path.splitext(filename)[1] == '.obb':
        actions.clean(['assets'], True)

        printer.info(f'Extracting assets from {filename}... ')
        actions.extract().assets(filename)

        printer.info('Renaming game assets... ')
        actions.rename().files('assets')
        actions.rename().dirs('assets')

        printer.info('Removing unneeded files... ')
        if os.path.splitext(filename)[1] == '.apk':
            actions.clean(['assets/renpy', 'assets/res'], False)
            actions.clean(['assets/dexopt'], True)

        printer.info('Renaming directory... ')
        actions.clean([os.path.splitext(filename)[0]], True)
        os.rename(os.path.join(output, 'assets'), os.path.splitext(filename)[0])
    else:
        Printer.err("It's not an .apk or .obb file!")
