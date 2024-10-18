from shutil import copyfile
import hashlib
import sys
import os


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

    def catch_unprocessed(self, source, output, error):
        self.copy_unprocessed(source, error)
        self.__errors += 1
        if not self.__params.hide_errors:
            self.__printer.error(f"File {os.path.split(source)[-1]} can't be processed! Error: {error}")

    def copy_unprocessed(self, source, output):
        if self.__params.copy_unprocessed:
            copyfile(source, output)
            self.__printer.info(f"File {os.path.split(source)[-1]} copied to compressed folder.")

    def catch_duplicates(self, path: str) -> str:
        if os.path.exists(path):
            new_path = os.path.splitext(path)[0] + "(vncopy)" + os.path.splitext(path)[1]
            self.__duplicates.append(new_path)
            return new_path
        return path

    def print_duplicates(self):
        for filename in self.__duplicates:
            self.__printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename}", '
                f'"{os.path.splitext(filename)[0] + "(vncopy)" + os.path.splitext(filename)[1]}"'
            )

    def out_rename(self, filename: str, target: str):
        if not self.__params.mimic_mode:
            dest_name = self.catch_duplicates(os.path.join(os.path.dirname(filename), target))
            os.rename(filename, dest_name)
        else:
            os.rename(filename, os.path.join(os.path.dirname(filename), target))
