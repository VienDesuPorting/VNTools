from ffmpeg import FFmpeg, FFmpegError
from PIL import Image
import pillow_avif
import os


class File:

    @staticmethod
    def get_type(filename):

        extensions = {
            "audio": ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma'],
            "image": ['.apng', '.avif', '.bmp', '.tga', '.tiff', '.dds', '.svg', '.webp', '.jpg', '.jpeg', '.png'],
            "video": ['.3gp' '.amv', '.avi', '.m2t', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv',
                      '.webm', '.ogv']
        }

        for file_type in extensions:
            if os.path.splitext(filename)[1] in extensions[file_type]:
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

    def __init__(self, params, printer, utils):
        self.params = params
        self.printer = printer
        self.utils = utils

    def audio(self, in_dir, file, out_dir, extension):
        bit_rate = self.params.audio_bitrate
        out_file = self.utils.check_duplicates(in_dir, out_dir, f'{os.path.splitext(file)[0]}.{extension}')
        try:
            (FFmpeg()
             .input(f'{in_dir}/{file}')
             .option("hide_banner")
             .output(out_file,{"b:a": bit_rate, "loglevel": "error"})
             .execute()
             )
        except FFmpegError as e:
            self.utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
            self.utils.errors += 1
            if not self.params.hide_errors:
                self.printer.error(f"File {file} can't be processed! Error: {e}")
        self.printer.files(file, os.path.splitext(file)[0], extension, f"{bit_rate}")
        return out_file


    def video(self, in_dir, file, out_dir, extension):
        if not self.params.video_skip:
            out_file = self.utils.check_duplicates(in_dir, out_dir, f'{os.path.splitext(file)[0]}.{extension}')
            codec = self.params.video_codec
            crf = self.params.video_crf

            try:
                (FFmpeg()
                 .input(f'{in_dir}/{file}')
                 .option("hide_banner")
                 .option("hwaccel", "auto")
                 .output(out_file,{"codec:v": codec, "v:b": 0, "loglevel": "error"}, crf=crf)
                 .execute()
                 )
                self.printer.files(file, os.path.splitext(file)[0], extension, codec)
            except FFmpegError as e:
                self.utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
                self.utils.errors += 1
                if not self.params.hide_errors:
                    self.printer.error(f"File {file} can't be processed! Error: {e}")
            return out_file
        else:
            self.utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
            return f'{out_dir}/{os.path.splitext(file)[0]}.{extension}'


    def image(self, in_dir, file, out_dir, extension):
        quality = self.params.image_quality
        out_file = self.utils.check_duplicates(in_dir, out_dir, f"{os.path.splitext(file)[0]}.{extension}")
        try:
            image = Image.open(f'{in_dir}/{file}')

            if (extension == "jpg" or extension == "jpeg" or
                    (extension == "webp" and not self.params.webp_rgba)):
                if File.has_transparency(image):
                    self.printer.warning(f"{file} has transparency. Changing to fallback...")
                    extension = self.params.image_fall_ext

            if File.has_transparency(image):
                image.convert('RGBA')

            res_downscale = self.params.image_downscale
            if res_downscale != 1:
                width, height = image.size
                new_size = (int(width / res_downscale), int(height / res_downscale))
                image = image.resize(new_size)

            image.save(out_file,
                       optimize=True,
                       lossless=self.params.image_lossless,
                       quality=quality,
                       minimize_size=True)
            self.printer.files(file, os.path.splitext(file)[0], extension, f"{quality}%")
        except Exception as e:
            self.utils.add_unprocessed_file(f'{in_dir}/{file}', f'{out_dir}/{file}')
            self.utils.errors += 1
            if not self.params.hide_errors:
                self.printer.error(f"File {file} can't be processed! Error: {e}")
        return out_file


    def unknown(self, in_dir, filename, out_dir):
        if self.params.force_compress:
            self.printer.unknown_file(filename)
            out_file = self.utils.check_duplicates(in_dir, out_dir, filename)
            try:
                (FFmpeg()
                 .input(f'{in_dir}/{filename}')
                 .output(out_file)
                 .execute()
                 )
            except FFmpegError as e:
                self.utils.add_unprocessed_file(f'{in_dir}/{filename}', f'{out_dir}/{filename}')
                self.utils.errors += 1
                if not self.params.hide_errors:
                    self.printer.error(f"File {filename} can't be processed! Error: {e}")
            return out_file
        else:
            self.utils.add_unprocessed_file(f'{in_dir}/{filename}', f'{out_dir}/{filename}')
            return f'{out_dir}/{filename}'

    def compress(self, _dir, filename, source, output):
        match File.get_type(filename):
            case "audio":
                out_file = self.audio(_dir, filename, output, self.params.audio_ext)
            case "image":
                out_file = self.image(_dir, filename, output, self.params.image_ext)
            case "video":
                out_file = self.video(_dir, filename, output, self.params.video_ext)
            case "unknown":
                out_file = self.unknown(_dir, filename, output)

        if self.params.mimic_mode:
            self.utils.mimic_rename(out_file, f'{_dir}/{filename}', source)

        self.printer.bar.update()
        self.printer.bar.next()
