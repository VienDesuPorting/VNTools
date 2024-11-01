from shutil import copyfile
from pathlib import Path
import hashlib
import sys
import os

from vnrecode.printer import Printer
from vnrecode.params import Params


class Utils:
    """
    Class contains various methods for internal utility use
    """

    def __init__(self, params_inst: Params, printer_inst: Printer):
        self.__errors = 0
        self.__params = params_inst
        self.__printer = printer_inst
        self.__duplicates = {}

    @staticmethod
    def sys_pause():
        """
        Method calls pause for Windows cmd shell
        :return: None
        """
        if sys.platform == "win32":
            os.system("pause")

    @staticmethod
    def get_hash(filename: str) -> str:
        """
        Method returns 8 chars of md5 hash for filename
        :param filename: File name to get md5
        :return: 8 chars of md5 hash
        """
        return hashlib.md5(filename.encode()).hexdigest()[:8]

    def get_comp_subdir(self, folder: str) -> Path:
        """
        Method returns the Path from str, changing the source folder in it to a compressed one
        :param folder: source subfolder
        :return: Path object with compressed subfolder
        """
        return Path(folder.replace(str(self.__params.source), str(self.__params.dest), 1))

    def get_recode_status(self):
        """
        Method prints recoding results
        :return: None
        """
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
            source = sum(file.stat().st_size for file in self.__params.source.glob('**/*') if file.is_file())
            output = sum(file.stat().st_size for file in self.__params.dest.glob('**/*') if file.is_file())

            print(f"\nResult: {source/1024/1024:.2f}MB -> "
                  f"{output/1024/1024:.2f}MB ({(output - source)/1024/1024:.2f}MB)")
        except ZeroDivisionError:
            self.__printer.warning("Nothing compressed!")

    def catch_unprocessed(self, input_path: Path, output_path: Path, error):
        """
        Method processes files that have not been recoded due to an error and prints error to console
        if hide_errors parameter is False
        :param input_path: Path of unprocessed file
        :param output_path: Destination path of unprocessed file
        :param error: Recoding exception
        :return: None
        """
        self.copy_unprocessed(input_path, output_path)
        self.__errors += 1
        if not self.__params.hide_errors:
            self.__printer.error(f"File {input_path.name} can't be processed! Error: {error}")

    def copy_unprocessed(self, input_path: Path, output_path: Path):
        """
        Method copies an unprocessed file from the source folder to the destination folder
        :param input_path: Path of unprocessed file
        :param output_path: Destination path of unprocessed file
        :return: None
        """
        if self.__params.copy_unprocessed:
            copyfile(input_path, output_path)
            self.__printer.info(f"File {input_path.name} copied to compressed folder.")

    def catch_duplicates(self, path: Path) -> Path:
        """
        Method checks if file path exists and returns folder/filename(vncopy).ext path
        if duplicate founded
        :param path: Some file Path
        :return: Duplicate path name with (vncopy) on end
        """
        if path.is_file() and path.exists():
            orig_name = path.name.replace("(vncopy)", "")
            new_path = Path(path.parent, path.stem + "(vncopy)" + path.suffix)
            try: self.__duplicates[orig_name]
            except KeyError: self.__duplicates[orig_name] = []
            if not new_path.name in self.__duplicates[orig_name]:
                self.__duplicates[orig_name].append(new_path.name)
            return self.catch_duplicates(new_path)
        return path

    def print_duplicates(self):
        """
        Method prints message about all duplicates generated during recode process
        :return: None
        """
        for filename in self.__duplicates.keys():
            self.__printer.warning(
                f'Duplicate file has been found! Check manually this files - "{filename}", ' +
                ', '.join(self.__duplicates[filename])
            )

    def out_rename(self, out_path: Path, target: Path):
        """
        Method removes md5 hash from file name and changes file extension in dependence of mimic mode
        :param out_path: Recoded file Path
        :param target: Target filename
        :return: None
        """
        if not self.__params.mimic_mode:
            dest_name = self.catch_duplicates(Path(out_path.parent, target.stem+out_path.suffix))
            os.rename(out_path, dest_name)
        else:
            os.rename(out_path, Path(out_path.parent, target.name))
