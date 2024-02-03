#!/usr/bin/env python3
from PIL import Image
import colorama
import zipfile
import shutil
import os
import sys


def printer(msg, level):
    match level:
        case "info":
            print(f"\033[100m[INFO] {msg}\033[49m")
        case "warn":
            print(f"\033[93m[WARN]\033[0m {msg}\033[49m")
        case "err":
            print(f"\033[31m[ERROR]\033[0m {msg} Exiting...\033[49m")
            exit()


def extract_folder(zip_ref, path, dest):
    for content in zip_ref.namelist():
        if content.split('/')[0] == path:
            zip_ref.extract(content, dest)


def find_modern_icon(directory):
    icons = []
    for folder, folders, files in os.walk(directory):
        for file in os.listdir(folder):
            if os.path.splitext(file)[1] == ".png":
                image = Image.open(f"{folder}/{file}")
                if image.size[0] == 432 and image.size[1] == 432:
                    icons.append(f"{folder}/{file}")
    if len(icons) == 0:
        raise KeyError
    return icons


def extract_assets(file):
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            extract_folder(zip_ref, 'assets', '')
            if os.path.splitext(file)[1] == '.apk':
                try:
                    # ~Ren'Py 8, 7
                    extract_folder(zip_ref, 'res', 'assets')
                    for icon in find_modern_icon('assets/res'):
                        os.rename(icon, f"assets/{os.path.split(icon)[1]}")
                except KeyError:
                    try:
                        # ~Ren'Py 6
                        zip_ref.extract('res/drawable/icon.png', 'assets')
                        os.rename('assets/res/drawable/icon.png', 'assets/icon.png')
                    except KeyError:
                        printer("Icon not found. Maybe it is not supported apk?", "warn")
    except zipfile.BadZipFile:
        return printer("Cant extract .apk file!", "err")


def rename_files(directory):
    for dir_ in os.walk(directory):
        for file in dir_[2]:
            path = f'{dir_[0]}/{file}'
            folder = '/'.join(path.split('/')[:len(path.split('/')) - 1])
            newname = f'{path.split("/").pop().replace("x-", "")}'
            os.rename(path, f'{folder}/{newname}')


def rename_dirs(directory):
    dirs = []
    for dir_ in os.walk(directory):
        dirs.append(dir_[0])
    dirs.reverse()
    dirs.pop()
    for dir__ in dirs:
        folder = '/'.join(dir__.split('/')[:len(dir__.split('/')) - 1])
        newname = f'{dir__.split("/").pop().replace("x-", "")}'
        os.rename(dir__, f'{folder}/{newname}')


def remove_unneeded(names, ignore):
    for name in names:
        try:
            shutil.rmtree(name)
        except FileNotFoundError:
            if not ignore:
                printer(f"Path {name} not found!", "warn")


if __name__ == '__main__':
    if sys.platform == "win32":
        colorama.init()
    for filename in os.listdir(os.getcwd()):
        if os.path.splitext(filename)[1] == '.apk' or os.path.splitext(filename)[1] == '.obb':
            remove_unneeded(['assets'], True)
            printer(f'Extracting assets from {filename}... ', "info")
            extract_assets(filename)
            printer('Renaming game assets... ', "info")
            rename_files('assets')
            rename_dirs('assets')
            printer('Removing unneeded files... ', "info")
            if os.path.splitext(filename)[1] == '.apk':
                remove_unneeded(['assets/renpy', 'assets/res'], False)
                remove_unneeded(['assets/dexopt'], True)
            printer('Renaming directory... ', "info")
            remove_unneeded([os.path.splitext(filename)[0]], True)
            os.rename('assets', os.path.splitext(filename)[0])
