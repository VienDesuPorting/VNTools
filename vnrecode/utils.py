from shutil import copyfile
from pathlib import Path
import hashlib
import sys
import os

from vnrecode.printer import Printer
from vnrecode.params import Params


class Utils:

    def __init__(self, params_inst: Params, printer_inst: Printer):
        self.__errors = 0
        self.__params = params_inst
        self.__printer = printer_inst
        self.__duplicates = []

    @staticmethod
    def sys_pause():
        if sys.platform == "win32":
            os.system("pause")

    @staticmethod
    def get_size(directory: Path) -> int:
        total_size = 0
        for folder, folders, files in os.walk(directory):
            for file in files:
                path = Path(folder, file)
                if not path.is_symlink():
                    total_size += path.stat().st_size
        return total_size

    @staticmethod
    def get_hash(filename: str) -> str:
        return hashlib.md5(filename.encode()).hexdigest()[:8]

    def get_compression_status(self):
        source_len = 0
        output_len = 0

        for folder, folders, files in os.walk(self.__params.source):
            source_len += len(files)

        for folder, folders, files in os.walk(self.__params.dest):
            for file in files:
                if not file.count("(vncopy)"):
                    output_len += 1

        if self.__errors != 0:
            self.__printer.warning("Some files failed to compress!")

        if source_len == output_len:
            self.__printer.info("Success!")
        else:
            self.__printer.warning("Original and compressed folders are not identical!")
        try:
            source = self.get_size(self.__params.source)
            output = self.get_size(self.__params.dest)

            print(f"\nResult: {source/1024/1024:.2f}MB -> "
                  f"{output/1024/1024:.2f}MB ({(output - source)/1024/1024:.2f}MB)")
        except ZeroDivisionError:
            self.__printer.warning("Nothing compressed!")

    def catch_unprocessed(self, input_path: Path, output_path: Path, error):
        self.copy_unprocessed(input_path, output_path)
        self.__errors += 1
        if not self.__params.hide_errors:
            self.__printer.error(f"File {input_path.name} can't be processed! Error: {error}")

    def copy_unprocessed(self, input_path: Path, output_path: Path):
        if self.__params.copy_unprocessed:
            copyfile(input_path, output_path)
            self.__printer.info(f"File {input_path.name} copied to compressed folder.")

    def catch_duplicates(self, path: Path) -> Path:
        if path.exists():
            new_path = Path(path.stem + "(vncopy)" + path.suffix)
            self.__duplicates.append(new_path)
            return new_path
        return path

    def print_duplicates(self):
        for filename in self.__duplicates:
            self.__printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename.name}", '
                f'"{filename.stem + "(vncopy)" + filename.suffix}"'
            )

    def out_rename(self, out_path: Path, target: str):
        if not self.__params.mimic_mode:
            dest_name = self.catch_duplicates(Path(out_path.parent, target))
            os.rename(out_path, dest_name)
        else:
            os.rename(out_path, Path(out_path.parent, target))
