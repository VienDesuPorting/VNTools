from shutil import copyfile
from glob import glob
import sys
import os
import re

import fnmatch


class Utils:

    def __init__(self, params, printer):
        self.errors = 0
        self.params = params
        self.printer = printer
        self.duplicates = []

    @staticmethod
    def sys_pause():
        if sys.platform == "win32":
            os.system("pause")

    @staticmethod
    def get_size(directory: str) -> int:
        total_size = 0
        for folder, folders, files in os.walk(directory):
            for file in files:
                if not os.path.islink(os.path.join(folder, file)):
                    total_size += os.path.getsize(os.path.join(folder, file))
        return total_size

    def get_compression(self, source: str, output: str):
        try:
            source = self.get_size(source)
            output = self.get_size(output)

            print(f"\nResult: {source/1024/1024:.2f}MB -> "
                  f"{output/1024/1024:.2f}MB ({(output - source)/1024/1024:.2f}MB)")
        except ZeroDivisionError:
            self.printer.warning("Nothing compressed!")

    def get_compression_status(self, source: str):
        source_len = 0
        output_len = 0

        for folder, folders, files in os.walk(source):
            source_len += len(files)

        for folder, folders, files in os.walk(f'{source}_compressed'):
            for file in files:
                if not os.path.splitext(file)[1].count("(copy)"):
                    output_len += 1

        if self.errors != 0:
            self.printer.warning("Some files failed to compress!")

        if source_len == output_len:
            self.printer.info("Success!")
        else:
            self.printer.warning("Original and compressed folders are not identical!")
        self.get_compression(source, f"{source}_compressed")

    def add_unprocessed_file(self, source: str, output: str):
        if self.params.copy_unprocessed:
            filename = os.path.split(source)[-1]
            copyfile(source, output)
            self.printer.info(f"File {filename} copied to compressed folder.")

    def check_duplicates(self, source: str, output: str, filename: str) -> str:
        re_pattern = re.compile(os.path.splitext(filename)[0]+r".[a-zA-Z0-9]+$", re.IGNORECASE)
        duplicates = [name for name in os.listdir(source) if re_pattern.match(name)]

        if len(duplicates) > 1:
            if filename.lower() not in (duplicate.lower() for duplicate in self.duplicates):
                self.duplicates.append(filename)
                new_name = os.path.splitext(filename)[0] + "(vncopy)" + os.path.splitext(filename)[1]
                return os.path.join(output, new_name)
        return os.path.join(output, filename)

    def print_duplicates(self):
        for filename in self.duplicates:
            self.printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename}", '
                f'"{os.path.splitext(filename)[0] + "(vncopy)" + os.path.splitext(filename)[1]}"'
            )

    def mimic_rename(self, filename: str, target: str, source: str):
        if filename.count("(vncopy)"):
            orig_name = filename.replace("(vncopy)", "")
            index = self.duplicates.index(os.path.split(orig_name)[-1])
            self.duplicates[index] = os.path.split(target)[-1]
            target = os.path.splitext(target)[0] + "(vncopy)" + os.path.splitext(target)[1]

        os.rename(filename, target.replace(source, f"{source}_compressed"))