from ffmpeg import FFmpeg, FFmpegError
from PIL import Image
import pillow_avif
import os


class File:

    @staticmethod
    def get_type(filename):
        audio_ext = ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma']
        image_ext = ['.apng', '.avif', '.bmp', '.tga', '.tiff', '.dds', '.svg', '.webp', '.jpg', '.jpeg', '.png']
        video_ext = ['.3gp' '.amv', '.avi', '.m2t', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv',
                     '.webm', '.ogv']

        if os.path.splitext(filename)[1] in audio_ext:
            return "audio"
        elif os.path.splitext(filename)[1] in image_ext:
            return "image"
        elif os.path.splitext(filename)[1] in video_ext:
            return "video"
        else:
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

    def audio(self, folder, file, target_folder, extension):
        bitrate = self.params.audio_bitrate
        try:
            (FFmpeg()
             .input(f'{folder}/{file}')
             .option("hide_banner")
             .output(self.utils.check_duplicates(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'),
                     {"b:a": bitrate, "loglevel": "error"})
             .execute()
             )
        except FFmpegError as e:
            self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
            self.utils.errors += 1
            if not self.params.hide_errors:
                self.printer.error(f"File {file} can't be processed! Error: {e}")
        self.printer.files(file, os.path.splitext(file)[0], extension, f"{bitrate}")
        return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


    def video(self, folder, file, target_folder, extension):
        if not self.params.video_skip:
            codec = self.params.video_codec
            crf = self.params.video_crf

            try:
                (FFmpeg()
                 .input(f'{folder}/{file}')
                 .option("hide_banner")
                 .option("hwaccel", "auto")
                 .output(self.utils.check_duplicates(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'),
                         {"codec:v": codec, "v:b": 0, "loglevel": "error"}, crf=crf)
                 .execute()
                 )
                self.printer.files(file, os.path.splitext(file)[0], extension, codec)
            except FFmpegError as e:
                self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
                self.utils.errors += 1
                if not self.params.hide_errors:
                    self.printer.error(f"File {file} can't be processed! Error: {e}")
        else:
            self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
        return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


    def image(self, folder, file, target_folder, extension):
        quality = self.params.image_quality
        try:
            image = Image.open(f'{folder}/{file}')

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

            image.save(self.utils.check_duplicates(f"{target_folder}/{os.path.splitext(file)[0]}.{extension}"),
                       optimize=True,
                       lossless=self.params.image_lossless,
                       quality=quality,
                       minimize_size=True)
            self.printer.files(file, os.path.splitext(file)[0], extension, f"{quality}%")
        except Exception as e:
            self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
            self.utils.errors += 1
            if not self.params.hide_errors:
                self.printer.error(f"File {file} can't be processed! Error: {e}")
        return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


    def unknown(self, folder, file, target_folder):
        if self.params.force_compress:
            self.printer.unknown_file(file)
            try:
                (FFmpeg()
                 .input(f'{folder}/{file}')
                 .output(self.utils.check_duplicates(f'{target_folder}/{file}'))
                 .execute()
                 )
            except FFmpegError as e:
                self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
                self.utils.errors += 1
                if not self.params.hide_errors:
                    self.printer.error(f"File {file} can't be processed! Error: {e}")
        else:
            self.utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
        return f'{target_folder}/{file}'


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
            try:
                os.rename(out_file, f'{_dir}/{filename}'.replace(source, f"{source}_compressed"))
            except FileNotFoundError:
                self.printer.warning(f"File {out_file} failed to copy to out dir")

        self.printer.bar.update()
        self.printer.bar.next()
