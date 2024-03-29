from modules import printer
from PIL import Image
import tomllib
import os

audio_exts = ['.aac', '.flac', '.m4a', '.mp3', '.ogg', '.opus', '.raw', '.wav', '.wma']
image_exts = ['.apng', '.avif', '.jfif', '.pjpeg', '.pjp', '.svg', '.webp', '.jpg', '.jpeg', '.png', '.raw']
video_exts = ['.3gp' '.amv', '.avi', '.gif', '.m4v', '.mkv', '.mov', '.mp4', '.m4v', '.mpeg', '.mpv', '.webm', '.ogv']

try:
    config = tomllib.load(open("ffmpeg-comp.toml", "rb"))
except FileNotFoundError:
    try:
        config = tomllib.load(open("/etc/ffmpeg-comp.toml", "rb"))
    except FileNotFoundError:
        printer.error("Config file not found. Please put it next to binary or in to /etc folder.")
        exit()

ffmpeg_params = config['FFMPEG']['FFmpegParams']
req_audio_ext = config['AUDIO']['Extension']
req_image_ext = config['IMAGE']['Extension']
req_video_ext = config['VIDEO']['Extension']


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


def compress(root_folder, folder):
    target_folder = folder.replace(root_folder, f"{root_folder}_compressed")
    for file in os.listdir(folder):
        if os.path.isfile(f'{folder}/{file}'):
            if os.path.splitext(file)[1] in audio_exts:

                bitrate = config['AUDIO']['BitRate']
                printer.files(file, os.path.splitext(file)[0], req_audio_ext, f"{bitrate}bit/s")
                os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} "
                          f"'{target_folder}/{os.path.splitext(file)[0]}.{req_audio_ext}'")

            elif os.path.splitext(file)[1] in image_exts:

                if req_image_ext == "jpg" or req_image_ext == "jpeg":

                    if not has_transparency(Image.open(f'{folder}/{file}')):
                        jpg_comp = config['IMAGE']['JpegComp']
                        printer.files(file, os.path.splitext(file)[0], req_image_ext, f"level {jpg_comp}")
                        os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -q {jpg_comp} "
                                  f"'{target_folder}/{os.path.splitext(file)[0]}.{req_image_ext}'")

                    else:
                        printer.warning(f"{file} has transparency (.jpg not support it). Skipping...")

                else:
                    comp_level = config['IMAGE']['CompLevel']
                    printer.files(file, os.path.splitext(file)[0], req_image_ext, f"{comp_level}%")
                    os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -compression_level {comp_level} "
                              f"'{target_folder}/{os.path.splitext(file)[0]}.{req_image_ext}'")

            elif os.path.splitext(file)[1] in video_exts:
                codec = config['VIDEO']['Codec']
                printer.files(file, os.path.splitext(file)[0], req_video_ext, codec)
                os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} -vcodec {codec} "
                          f"'{target_folder}/{os.path.splitext(file)[0]}.{req_video_ext}'")

            else:
                printer.warning("File extension not recognized. This may affect the quality of the compression.")
                printer.unknown_file(file)
                os.system(f"ffmpeg -i '{folder}/{file}' {ffmpeg_params} '{target_folder}/{file}'")
