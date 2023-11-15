from modules import configloader
from modules import printer
from modules import utils
from PIL import Image
import pillow_avif
import ffmpeg
import os


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

    printer.files(file, os.path.splitext(file)[0], extension, f"{bitrate}")
    try:
        (ffmpeg
         .input(f'{folder}/{file}')
         .output(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}', audio_bitrate=bitrate)
         .run(quiet=True)
         )
    except ffmpeg._run.Error:
        utils.errors_count += 1
        if not configloader.config['FFMPEG']['HideErrors']:
            printer.error(f"File {file} can't be processed! Maybe it is ffmpeg error or unsupported file.")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress_video(folder, file, target_folder, extension):
    codec = configloader.config['VIDEO']['Codec']

    printer.files(file, os.path.splitext(file)[0], extension, codec)
    try:
        (ffmpeg
         .input(f'{folder}/{file}')
         .output(f'{target_folder}/{os.path.splitext(file)[0]}.{extension}', format=codec)
         .run(quiet=True)
         )
    except ffmpeg._run.Error:
        utils.errors_count += 1
        if not configloader.config['FFMPEG']['HideErrors']:
            printer.error(f"File {file} can't be processed! Maybe it is ffmpeg error or unsupported file.")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress_image(folder, file, target_folder, extension):
    quality = configloader.config['IMAGE']['Quality']

    image = Image.open(f'{folder}/{file}')

    if (extension == "jpg" or extension == "jpeg" or
            (extension == "webp" and not configloader.config['FFMPEG']['WebpRGBA'])):

        if has_transparency(Image.open(f'{folder}/{file}')):
            printer.warning(f"{file} has transparency. Changing to png...")
            printer.files(file, os.path.splitext(file)[0], "png", f"{quality}%")
            image.save(f"{target_folder}/{os.path.splitext(file)[0]}.png",
                       optimize=True,
                       quality=quality)
            return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'

    else:
        printer.files(file, os.path.splitext(file)[0], extension, f"{quality}%")
        image.save(f"{target_folder}/{os.path.splitext(file)[0]}.{extension}",
                   optimize=True,
                   quality=quality)
    return f'{target_folder}/{os.path.splitext(file)[0]}.{extension}'


def compress(folder, file, target_folder):
    printer.unknown_file(file)
    try:
        (ffmpeg
         .input(f'{folder}/{file}')
         .output(f'{target_folder}/{file}')
         .run(quiet=True)
         )
    except ffmpeg._run.Error:
        utils.errors_count += 1
        if not configloader.config['FFMPEG']['HideErrors']:
            printer.error(f"File {file} can't be processed! Maybe it is ffmpeg error or unsupported file.")
    return f'{target_folder}/{file}'
