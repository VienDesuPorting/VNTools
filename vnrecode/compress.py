from ffmpeg import FFmpeg, FFmpegError
from PIL import Image
from os import path
import pillow_avif

from .printer import Printer
from .params import Params
from .utils import Utils


class File:

    @staticmethod
    def get_type(filename: str) -> str:

        extensions = {
            "audio": ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma'],
            "image": ['.apng', '.avif', '.bmp', '.tga', '.tiff', '.dds', '.svg', '.webp', '.jpg', '.jpeg', '.png'],
            "video": ['.3gp' '.amv', '.avi', '.m2t', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv',
                      '.webm', '.ogv']
        }

        for file_type in extensions:
            if path.splitext(filename)[1] in extensions[file_type]:
                return file_type
        return "unknown"

    @staticmethod
    def has_transparency(img: Image) -> bool:
        if img.info.get("transparency", None) is not None:
            return True
        if img.mode == "P":
            transparent = img.info.get("transparency", -1)
            for _, index in img.getcolors():
                if index == transparent:
                    return True
        elif img.mode == "RGBA":
            extrema = img.getextrema()
            if extrema[3][0] < 255:
                return True
        return False


class Compress:

    def __init__(self, params: Params, printer: Printer, utils: Utils):
        self.__params = params
        self.__printer = printer
        self.__utils = utils

    def audio(self, in_dir: str, file: str, out_dir: str, extension: str) -> str:
        bit_rate = self.__params.audio_bitrate
        out_file = self.__utils.check_duplicates(in_dir, out_dir, f'{path.splitext(file)[0]}.{extension}')
        try:
            (FFmpeg()
             .input(path.join(in_dir, file))
             .option("hide_banner")
             .output(out_file,{"b:a": bit_rate, "loglevel": "error"})
             .execute()
             )
        except FFmpegError as e:
            self.__utils.add_unprocessed_file(path.join(in_dir, file), path.join(out_dir, file))
            self.__utils.errors += 1
            if not self.__params.hide_errors:
                self.__printer.error(f"File {file} can't be processed! Error: {e}")
        self.__printer.files(file, path.splitext(file)[0], extension, f"{bit_rate}")
        return out_file

    def video(self, in_dir: str, file: str, out_dir: str, extension: str) -> str:
        if not self.__params.video_skip:
            out_file = self.__utils.check_duplicates(in_dir, out_dir, f'{path.splitext(file)[0]}.{extension}')
            codec = self.__params.video_codec
            crf = self.__params.video_crf

            try:
                (FFmpeg()
                 .input(path.join(in_dir, file))
                 .option("hide_banner")
                 .option("hwaccel", "auto")
                 .output(out_file,{"codec:v": codec, "v:b": 0, "loglevel": "error"}, crf=crf)
                 .execute()
                 )
                self.__printer.files(file, path.splitext(file)[0], extension, codec)
            except FFmpegError as e:
                self.__utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
                self.__utils.errors += 1
                if not self.__params.hide_errors:
                    self.__printer.error(f"File {file} can't be processed! Error: {e}")
            return out_file
        else:
            self.__utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
            return f'{out_dir}/{path.splitext(file)[0]}.{extension}'

    def image(self, in_dir: str, file: str, out_dir: str, extension: str) -> str:
        quality = self.__params.image_quality
        out_file = self.__utils.check_duplicates(in_dir, out_dir, f"{path.splitext(file)[0]}.{extension}")
        try:
            image = Image.open(path.join(in_dir, file))

            if (extension == "jpg" or extension == "jpeg" or
                    (extension == "webp" and not self.__params.webp_rgba)):
                if File.has_transparency(image):
                    self.__printer.warning(f"{file} has transparency. Changing to fallback...")
                    extension = self.__params.image_fall_ext

            if File.has_transparency(image):
                image.convert('RGBA')

            res_downscale = self.__params.image_downscale
            if res_downscale != 1:
                width, height = image.size
                new_size = (int(width / res_downscale), int(height / res_downscale))
                image = image.resize(new_size)

            image.save(out_file,
                       optimize=True,
                       lossless=self.__params.image_lossless,
                       quality=quality,
                       minimize_size=True)
            self.__printer.files(file, path.splitext(file)[0], extension, f"{quality}%")
        except Exception as e:
            self.__utils.add_unprocessed_file(path.join(in_dir, file), path.join(out_dir, file))
            self.__utils.errors += 1
            if not self.__params.hide_errors:
                self.__printer.error(f"File {file} can't be processed! Error: {e}")
        return out_file

    def unknown(self, in_dir: str, filename: str, out_dir: str) -> str:
        if self.__params.force_compress:
            self.__printer.unknown_file(filename)
            out_file = self.__utils.check_duplicates(in_dir, out_dir, filename)
            try:
                (FFmpeg()
                 .input(path.join(in_dir, filename))
                 .output(out_file)
                 .execute()
                 )
            except FFmpegError as e:
                self.__utils.add_unprocessed_file(path.join(in_dir, filename), path.join(out_dir, filename))
                self.__utils.errors += 1
                if not self.__params.hide_errors:
                    self.__printer.error(f"File {filename} can't be processed! Error: {e}")
            return out_file
        else:
            self.__utils.add_unprocessed_file(path.join(in_dir, filename), path.join(out_dir, filename))
            return path.join(out_dir, filename)

    def compress(self, dir_: str, filename: str, output: str):
        match File.get_type(filename):
            case "audio":
                out_file = self.audio(dir_, filename, output, self.__params.audio_ext)
            case "image":
                out_file = self.image(dir_, filename, output, self.__params.image_ext)
            case "video":
                out_file = self.video(dir_, filename, output, self.__params.video_ext)
            case "unknown":
                out_file = self.unknown(dir_, filename, output)

        if self.__params.mimic_mode:
            self.__utils.mimic_rename(out_file, path.join(dir_, filename))

        self.__printer.bar.update()
        self.__printer.bar.next()
