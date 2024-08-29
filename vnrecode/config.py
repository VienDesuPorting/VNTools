from argparse import Namespace, ArgumentParser
from dataclasses import dataclass
from sysconfig import get_path
from typing import Any
import tomllib
import os


@dataclass
class Config:

    config: dict[str, Any]
    args: Namespace

    @classmethod
    def setup_config(cls):
        default_config = os.path.join(get_path('purelib'), "vnrecode", "vnrecode.toml")
        parser = ArgumentParser(prog="vnrecode",
                                description="Python utility to compress Visual Novel Resources"
                                )
        parser.add_argument("source", help="SourceDir")
        parser.add_argument("-c", "--config", default=default_config, help="ConfigFile")
        parser.add_argument("-u", action="store_true", help="CopyUnprocessed")
        parser.add_argument("-f", "--force", action="store_true", help="ForceCompress")
        parser.add_argument("-m", "--mimic", action="store_true", help="MimicMode")
        parser.add_argument("-s", "--silent", action="store_true", help="HideErrors")
        parser.add_argument("--webprgba", action="store_true", help="WebpRGBA")
        parser.add_argument("-j", "--jobs", type=int, help="Workers")
        parser.add_argument("-ae", "--aext", help="Audio Extension")
        parser.add_argument("-ab", "--abit", help="Audio Bitrate")
        parser.add_argument("-id", "--idown", type=int, help="Image Downscale")
        parser.add_argument("-ie", "--iext", help="Image Extension")
        parser.add_argument("-ife", "--ifallext", help="Image Fallback Extension")
        parser.add_argument("-il", "--ilossless", action="store_true", help="Image Lossless")
        parser.add_argument("-iq", "--iquality", help="Image Quality")
        parser.add_argument("--vcrf", help="Video CRF")
        parser.add_argument("-vs", "--vskip", help="Video Skip")
        parser.add_argument("-ve", "--vext", help="Video Extension")
        parser.add_argument("-vc", "--vcodec", help="Video Codec")

        args = parser.parse_args()
        if os.path.isfile(args.config):
            with open(args.config, "rb") as cfile:
                config = tomllib.load(cfile)
        else:
            print("Failed to find config. Check `vnrecode -h` to more info")
            exit(255)
        return cls(config=config, args=args)
