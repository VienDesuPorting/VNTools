from shutil import copyfile
import sys
import os
import re


class Utils:

    def __init__(self, params_inst, printer_inst):
        self.__errors = 0
        self.__params = params_inst
        self.__printer = printer_inst
        self.__duplicates = []

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

    def get_compression_status(self):
        source_len = 0
        output_len = 0

        for folder, folders, files in os.walk(self.__params.source):
            source_len += len(files)

        for folder, folders, files in os.walk(self.__params.dest):
            for file in files:
                if not os.path.splitext(file)[1].count("(vncopy)"):
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

    def add_unprocessed_file(self, source: str, output: str):
        if self.__params.copy_unprocessed:
            filename = os.path.split(source)[-1]
            copyfile(source, output)
            self.__printer.info(f"File {filename} copied to compressed folder.")

    def check_duplicates(self, source: str, output: str, filename: str) -> str:
        re_pattern = re.compile(os.path.splitext(filename)[0]+r".[a-zA-Z0-9]+$", re.IGNORECASE)
        duplicates = [name for name in os.listdir(source) if re_pattern.match(name)]

        if len(duplicates) > 1:
            if filename.lower() not in (duplicate.lower() for duplicate in self.__duplicates):
                self.__duplicates.append(filename)
                new_name = os.path.splitext(filename)[0] + "(vncopy)" + os.path.splitext(filename)[1]
                return os.path.join(output, new_name)
        return os.path.join(output, filename)

    def print_duplicates(self):
        for filename in self.__duplicates:
            self.__printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename}", '
                f'"{os.path.splitext(filename)[0] + "(vncopy)" + os.path.splitext(filename)[1]}"'
            )

    def mimic_rename(self, filename: str, target: str):
        if filename.count("(vncopy)"):
            orig_name = filename.replace("(vncopy)", "")
            index = self.__duplicates.index(os.path.split(orig_name)[-1])
            self.__duplicates[index] = os.path.split(target)[-1]
            target = os.path.splitext(target)[0] + "(vncopy)" + os.path.splitext(target)[1]

        os.rename(filename, target.replace(self.__params.source, self.__params.dest))