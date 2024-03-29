#!/bin/python3
import zipfile
import os
import shutil


def extract_assets(file):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        for content in zip_ref.namelist():
            if content.split('/')[0] == 'assets':
                zip_ref.extract(content)
        if os.path.splitext(file)[1] == '.apk':
            try:
                zip_ref.extract('res/mipmap-xxxhdpi-v4/icon_background.png', 'assets')
                zip_ref.extract('res/mipmap-xxxhdpi-v4/icon_foreground.png', 'assets')
                os.rename('assets/res/mipmap-xxxhdpi-v4/icon_background.png', 'assets/android-icon_background.png')
                os.rename('assets/res/mipmap-xxxhdpi-v4/icon_foreground.png', 'assets/android-icon_foreground.png')
            except KeyError:
                zip_ref.extract('res/drawable/icon.png', 'assets')
                os.rename('assets/res/drawable/icon.png', 'assets/icon.png')


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


if __name__ == '__main__':
    for filename in os.listdir(os.getcwd()):
        renpy_warn = 0
        if os.path.splitext(filename)[1] == '.apk' or os.path.splitext(filename)[1] == '.obb':
            print(f'[INFO] Extracting assets from {filename}... ', end='')
            extract_assets(filename)
            print('Done')
            print('[INFO] Renaming game assets... ', end='')
            rename_files('assets')
            rename_dirs('assets')
            print('Done')
            print('[INFO] Removing unneeded files... ', end='')
            try:
                shutil.rmtree('assets/renpy')
            except FileNotFoundError:
                renpy_warn = 1
            if os.path.splitext(filename)[1] == '.apk':
                shutil.rmtree('assets/res')
            print('Done')
            if renpy_warn:
                print("[WARN] File does not contain renpy folder!")
            print('[INFO] Renaming directory... ', end='')
            os.rename('assets', f'{os.path.splitext(filename)[0]}')
            print('Done')
