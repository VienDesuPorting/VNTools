from shutil import copyfile
import sys
import os

class Utils:

    def __init__(self, params, printer):
        self.errors = 0
        self.params = params
        self.printer = printer

    @staticmethod
    def sys_pause():
        if sys.platform == "win32":
            os.system("pause")

    @staticmethod
    def get_size(directory):
        total_size = 0
        for folder, folders, files in os.walk(directory):
            for file in files:
                if not os.path.islink(f"{folder}/{file}"):
                    total_size += os.path.getsize(f"{folder}/{file}")
        return total_size

    def get_compression(self, source, output):
        try:
            source = self.get_size(source)
            output = self.get_size(output)

            print(f"\nResult: {source/1024/1024:.2f}MB -> "
                  f"{output/1024/1024:.2f}MB ({(output - source)/1024/1024:.2f}MB)")
        except ZeroDivisionError:
            self.printer.warning("Nothing compressed!")

    def get_compression_status(self, orig_folder):
        orig_folder_len = 0
        comp_folder_len = 0

        for folder, folders, files in os.walk(orig_folder):
            orig_folder_len += len(files)

        for folder, folders, files in os.walk(f'{orig_folder}_compressed'):
            for file in files:
                if not os.path.splitext(file)[1].count("(copy)"):
                    comp_folder_len += 1

        if self.errors != 0:
            self.printer.warning("Some files failed to compress!")

        if orig_folder_len == comp_folder_len:
            self.printer.info("Success!")
            self.get_compression(orig_folder, f"{orig_folder}_compressed")
        else:
            self.printer.warning("Original and compressed folders are not identical!")
            self.get_compression(orig_folder, f"{orig_folder}_compressed")

    def add_unprocessed_file(self, orig_folder, new_folder):
        if self.params.copy_unprocessed:
            filename = orig_folder.split("/").pop()
            copyfile(orig_folder, new_folder)
            self.printer.info(f"File {filename} copied to compressed folder.")

    def check_duplicates(self, new_folder):
        filename = new_folder.split().pop()
        if os.path.exists(new_folder):
            self.printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename}", '
                f'"{os.path.splitext(filename)[0] + "(copy)" + os.path.splitext(filename)[1]}"')
            return os.path.splitext(new_folder)[0] + "(copy)" + os.path.splitext(new_folder)[1]
        return new_folder
