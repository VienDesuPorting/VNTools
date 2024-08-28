from zipfile import ZipFile, BadZipFile
from PIL import Image
import shutil
import os

from .printer import Printer


class Extract:

    def __init__(self, output: str):
        self.output = output

    @staticmethod
    def folder(zip_ref: ZipFile, path: str, dest: str):
        for content in zip_ref.namelist():
            if content.split('/')[0] == path:
                zip_ref.extract(content, dest)

    @staticmethod
    def icon(directory: str):
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

    def assets(self, file: str):
        try:
            with ZipFile(file, 'r') as zip_ref:
                self.folder(zip_ref, 'assets', self.output)
                if os.path.splitext(file)[1] == '.apk':
                    try:
                        # ~Ren'Py 8, 7
                        self.folder(zip_ref, 'res', os.path.join(self.output, 'assets'))
                        for icon in self.icon(os.path.join(self.output, 'assets/res')):
                            os.rename(icon, os.path.join(self.output, "assets", os.path.split(icon)[1]))
                    except KeyError:
                        try:
                            # ~Ren'Py 6
                            zip_ref.extract('res/drawable/icon.png', os.path.join(self.output, 'assets'))
                            os.rename(os.path.join(self.output, 'assets/res/drawable/icon.png'),
                                      os.path.join(self.output, 'assets/icon.png'))
                        except KeyError:
                            Printer.warn("Icon not found. Maybe it is not supported apk?")
        except BadZipFile:
            Printer.err("Cant extract .apk file!")


class Rename:

    def __init__(self, output):
        self.output = output

    def files(self, directory: str):
        for dir_ in os.walk(os.path.join(self.output, directory)):
            for file in dir_[2]:
                path = f'{dir_[0]}/{file}'
                folder = '/'.join(path.split('/')[:len(path.split('/')) - 1])
                newname = f'{path.split("/").pop().replace("x-", "")}'
                os.rename(path, f'{folder}/{newname}')

    def dirs(self, directory: str):
        dirs = []
        for dir_ in os.walk(os.path.join(self.output, directory)):
            dirs.append(dir_[0])
        dirs.reverse()
        dirs.pop()
        for dir__ in dirs:
            folder = '/'.join(dir__.split('/')[:len(dir__.split('/')) - 1])
            newname = f'{dir__.split("/").pop().replace("x-", "")}'
            os.rename(dir__, f'{folder}/{newname}')


class Actions:

    def __init__(self, output: str):
        self.output = output

    def extract(self) -> Extract:
        return Extract(self.output)

    def rename(self) -> Rename:
        return Rename(self.output)

    def clean(self, names: list, ignore: bool):
        for name in names:
            name = os.path.join(self.output, name)
            try:
                shutil.rmtree(name)
            except FileNotFoundError:
                if not ignore:
                    Printer.warn(f"Path {name} not found!")
