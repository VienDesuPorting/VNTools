from ffmpeg import FFmpeg, FFmpegError
from pathlib import Path
from PIL import Image
import pillow_avif

from .printer import Printer
from .params import Params
from .utils import Utils


class File:

    @staticmethod
    def get_type(filename: Path) -> str:

        extensions = {
            "audio": ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma'],
            "image": ['.apng', '.avif', '.bmp', '.tga', '.tiff', '.dds', '.svg', '.webp', '.jpg', '.jpeg', '.png'],
            "video": ['.3gp' '.amv', '.avi', '.m2t', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv',
                      '.webm', '.ogv']
        }

        for file_type in extensions:
            if filename.suffix in extensions[file_type]:
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

    def __init__(self, params_inst: Params, printer_inst: Printer, utils_inst: Utils):
        self.__params = params_inst
        self.__printer = printer_inst
        self.__utils = utils_inst

    def audio(self, input_path: Path, output_dir: Path, extension: str) -> Path:
        bit_rate = self.__params.audio_bitrate
        prefix = self.__utils.get_hash(input_path.name)
        out_file = Path(output_dir, f'{prefix}_{input_path.stem}.{extension}')
        try:
            (FFmpeg()
             .input(input_path)
             .option("hide_banner")
             .output(out_file,{"b:a": bit_rate, "loglevel": "error"})
             .execute()
             )
        except FFmpegError as e:
            self.__utils.catch_unprocessed(input_path, out_file, e)
        self.__printer.files(input_path, out_file, f"{bit_rate}")
        return out_file

    def image(self, input_path: Path, output_dir: Path, extension: str) -> Path:
        quality = self.__params.image_quality
        prefix = self.__utils.get_hash(input_path.name)
        out_file = Path(output_dir, f"{prefix}_{input_path.stem}.{extension}")
        try:
            image = Image.open(input_path)

            if (extension == "jpg" or extension == "jpeg" or
                    (extension == "webp" and not self.__params.webp_rgba)):
                if File.has_transparency(image):
                    self.__printer.warning(f"{input_path.name} has transparency. Changing to fallback...")
                    out_file = Path(output_dir, f"{prefix}_{input_path.stem}.{self.__params.image_fall_ext}")

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
            self.__printer.files(input_path, out_file, f"{quality}%")
        except Exception as e:
            self.__utils.catch_unprocessed(input_path, out_file, e)
        return out_file

    def video(self, input_path: Path, output_dir: Path, extension: str) -> Path:
        prefix = self.__utils.get_hash(input_path.name)
        out_file = Path(output_dir, f'{prefix}_{input_path.stem}.{extension}')
        if not self.__params.video_skip:
            codec = self.__params.video_codec
            crf = self.__params.video_crf

            try:
                (FFmpeg()
                 .input(input_path)
                 .option("hide_banner")
                 .option("hwaccel", "auto")
                 .output(out_file,{"codec:v": codec, "v:b": 0, "loglevel": "error"}, crf=crf)
                 .execute()
                 )
                self.__printer.files(input_path, out_file, codec)
            except FFmpegError as e:
                self.__utils.catch_unprocessed(input_path, out_file, e)
        else:
            self.__utils.copy_unprocessed(input_path, out_file)
        return out_file

    def unknown(self, input_path: Path, output_dir: Path) -> Path:
        prefix = self.__utils.get_hash(input_path.name)
        out_file = Path(output_dir, f"{prefix}_{input_path.name}")
        if self.__params.force_compress:
            self.__printer.unknown_file(input_path.name)
            try:
                (FFmpeg()
                 .input(input_path)
                 .output(out_file)
                 .execute()
                 )
            except FFmpegError as e:
                self.__utils.catch_unprocessed(input_path, out_file, e)
        else:
            self.__utils.copy_unprocessed(input_path, out_file)
        return out_file

    def compress(self, source: Path, output: Path):
        match File.get_type(source):
            case "audio":
                out_file = self.audio(source, output, self.__params.audio_ext)
            case "image":
                out_file = self.image(source, output, self.__params.image_ext)
            case "video":
                out_file = self.video(source, output, self.__params.video_ext)
            case "unknown":
                out_file = self.unknown(source, output)

        self.__utils.out_rename(out_file, source.name)
        self.__printer.bar.update()
        self.__printer.bar.next()
