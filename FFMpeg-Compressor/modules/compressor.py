from modules import configloader
from modules import printer
from modules import utils
from PIL import Image
import pillow_avif
from ffmpeg import FFmpeg, FFmpegError
import os


def get_file_type(filename):
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


def has_transparency(img):
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


def compress_audio(folder, file, target_folder, extension):
    bitrate = configloader.config['AUDIO']['BitRate']
    try:
        (FFmpeg()
         .input(f'{folder}/{file}')
         .option("hide_banner")
         .output(utils.check_duplicates(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'),
                 {"b:a": bitrate, "loglevel": "error"})
         .execute()
         )
    except FFmpegError as e:
        utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
        utils.errors_count += 1
        if not configloader.config['FFMPEG']['HideErrors']:
            printer.error(f"File {file} can't be processed! Error: {e}")
    printer.files(file, os.path.splitext(file)[0], extension, f"{bitrate}")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress_video(folder, file, target_folder, extension):
    if not configloader.config['VIDEO']['SkipVideo']:
        codec = configloader.config['VIDEO']['Codec']
        crf = configloader.config['VIDEO']['CRF']

        try:
            (FFmpeg()
             .input(f'{folder}/{file}')
             .option("hide_banner")
             .option("hwaccel", "auto")
             .output(utils.check_duplicates(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'),
                     {"codec:v": codec, "v:b": 0, "loglevel": "error"}, crf=crf)
             .execute()
             )
            printer.files(file, os.path.splitext(file)[0], extension, codec)
        except FFmpegError as e:
            utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
            utils.errors_count += 1
            if not configloader.config['FFMPEG']['HideErrors']:
                printer.error(f"File {file} can't be processed! Error: {e}")
    else:
        utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress_image(folder, file, target_folder, extension):
    quality = configloader.config['IMAGE']['Quality']
    try:
        image = Image.open(f'{folder}/{file}')

        if (extension == "jpg" or extension == "jpeg" or
                (extension == "webp" and not configloader.config['FFMPEG']['WebpRGBA'])):
            if has_transparency(image):
                printer.warning(f"{file} has transparency. Changing to fallback...")
                extension = configloader.config['IMAGE']['FallBackExtension']

        if has_transparency(image):
            image.convert('RGBA')

        res_downscale = configloader.config['IMAGE']['ResDownScale']
        if res_downscale != 1:
            width, height = image.size
            new_size = (int(width / res_downscale), int(height / res_downscale))
            image = image.resize(new_size)

        image.save(utils.check_duplicates(f"{target_folder}/{os.path.splitext(file)[0]}.{extension}"),
                   optimize=True,
                   lossless=configloader.config['IMAGE']['Lossless'],
                   quality=quality,
                   minimize_size=True)
        printer.files(file, os.path.splitext(file)[0], extension, f"{quality}%")
    except Exception as e:
        utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
        utils.errors_count += 1
        if not configloader.config['FFMPEG']['HideErrors']:
            printer.error(f"File {file} can't be processed! Error: {e}")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress(folder, file, target_folder):
    if configloader.config["FFMPEG"]["ForceCompress"]:
        printer.unknown_file(file)
        try:
            (FFmpeg()
             .input(f'{folder}/{file}')
             .output(f'{target_folder}/{file}')
             .execute()
             )
        except FFmpegError as e:
            utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
            utils.errors_count += 1
            if not configloader.config['FFMPEG']['HideErrors']:
                printer.error(f"File {file} can't be processed! Error: {e}")
    else:
        utils.add_unprocessed_file(f'{folder}/{file}', f'{target_folder}/{file}')
    return f'{target_folder}/{file}'


def compress_file(_dir, filename, target_dir, source):
    match get_file_type(filename):
        case "audio":
            comp_file = compress_audio(_dir, filename, target_dir,
                                       configloader.config['AUDIO']['Extension'])
        case "image":
            comp_file = compress_image(_dir, filename, target_dir,
                                       configloader.config['IMAGE']['Extension'])
        case "video":
            comp_file = compress_video(_dir, filename, target_dir,
                                       configloader.config['VIDEO']['Extension'])
        case "unknown":
            comp_file = compress(_dir, filename, target_dir)

    if configloader.config['FFMPEG']['MimicMode']:
        try:
            os.rename(comp_file, f'{_dir}/{filename}'.replace(source, f"{source}_compressed"))
        except FileNotFoundError:
            pass

    printer.bar.update()
    printer.bar.next()
