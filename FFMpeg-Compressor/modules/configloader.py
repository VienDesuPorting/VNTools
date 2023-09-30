import tomllib
from modules import printer

try:
    config = tomllib.load(open("ffmpeg-comp.toml", "rb"))
except FileNotFoundError:
    try:
        config = tomllib.load(open("/etc/ffmpeg-comp.toml", "rb"))
    except FileNotFoundError:
        printer.error("Config file not found. Please put it next to binary or in to /etc folder.")
        exit()
