from modules import printer
from modules import configloader
from PIL import Image
import os


def get_req_ext(file):
    match get_file_type(file):
        case "audio":
            return configloader.config['AUDIO']['Extension']
        case "image":
            return configloader.config['IMAGE']['Extension']
        case "video":
            return configloader.config['VIDEO']['Extension']


def get_file_type(file):
    audio_ext = ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma']
    image_ext = ['.apng', '.avif', '.bmp', '.jfif', '.pjpeg', '.pjp', '.svg', '.webp', '.jpg', '.jpeg', '.png', '.raw']
    video_ext = ['.3gp' '.amv', '.avi', '.gif', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv', '.webm',
                  '.ogv']
    file_extension = os.path.splitext(file)[1]

    if file_extension in audio_ext:
        return "audio"
    elif file_extension in image_ext:
        return "image"
    elif file_extension in video_ext:
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


def compress_audio(folder, file, target_folder):
    ffmpeg_params = configloader.config['FFMPEG']['FFmpegParams']
    bitrate = configloader.config['AUDIO']['BitRate']

    printer.files(file, os.path.splitext(file)[0], get_req_ext(file), f"{bitrate}")
    os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -q:a {bitrate} "
              f"'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'


def compress_video(folder, file, target_folder):
    ffmpeg_params = configloader.config['FFMPEG']['FFmpegParams']
    codec = configloader.config['VIDEO']['Codec']

    printer.files(file, os.path.splitext(file)[0], get_req_ext(file), codec)
    os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -vcodec {codec} "
              f"'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'


def compress_image(folder, file, target_folder):
    ffmpeg_params = configloader.config['FFMPEG']['FFmpegParams']
    comp_level = configloader.config['IMAGE']['CompLevel']
    jpg_comp = configloader.config['IMAGE']['JpegComp']

    if get_req_ext(file) == "jpg" or get_req_ext(file) == "jpeg":

        if not has_transparency(Image.open(f'{folder}/{file}')):
            printer.files(file, os.path.splitext(file)[0], get_req_ext(file), f"level {jpg_comp}")
            os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -q {jpg_comp} "
                      f"'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'")
        else:
            printer.warning(f"{file} has transparency (.jpg not support it). Skipping...")
    else:
        printer.files(file, os.path.splitext(file)[0], get_req_ext(file), f"{comp_level}%")
        os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -compression_level {comp_level} "
                  f"'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'")
    return f'{target_folder}/{os.path.splitext(file)[0]}.{get_req_ext(file)}'


def compress(folder, file, target_folder):
    ffmpeg_params = configloader.config['FFMPEG']['FFmpegParams']
    printer.unknown_file(file)
    os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} '{target_folder}/{file}'")
    return f'{target_folder}/{file}'
