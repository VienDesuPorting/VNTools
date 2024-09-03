from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Self
import tomllib
import os

@dataclass
class Params:

    copy_unprocessed: bool
    force_compress: bool
    mimic_mode: bool
    hide_errors: bool
    webp_rgba: bool
    workers: int

    audio_ext: str
    audio_bitrate: str

    image_downscale: int
    image_ext: str
    image_fall_ext: str
    image_lossless: str
    image_quality: int

    video_crf: int
    video_skip: bool
    video_ext: str
    video_codec: str

    source: str

    @classmethod
    def setup(cls) -> Self:
        parser = ArgumentParser(prog="vnrecode",
                                description="Python utility to compress Visual Novel Resources"
                                )
        parser.add_argument("source", help="SourceDir")
        parser.add_argument("-c", "--config", help="ConfigFile")
        parser.add_argument("-u", type=bool, help="CopyUnprocessed", default=True)
        parser.add_argument("-f", "--force", type=bool, help="ForceCompress", default=False)
        parser.add_argument("-m", "--mimic", type=bool, help="MimicMode", default=True)
        parser.add_argument("-s", "--silent", type=bool, help="HideErrors", default=True)
        parser.add_argument("--webprgba", type=bool, help="WebpRGBA", default=True)
        parser.add_argument("-j", "--jobs", type=int, help="Workers", default=16)
        parser.add_argument("-ae", "--aext", help="Audio Extension", default="opus")
        parser.add_argument("-ab", "--abit", help="Audio Bitrate", default="128k")
        parser.add_argument("-id", "--idown", type=int, help="Image Downscale", default=1)
        parser.add_argument("-ie", "--iext", help="Image Extension", default="avif")
        parser.add_argument("-ife", "--ifallext", help="Image Fallback Extension", default="webp")
        parser.add_argument("-il", "--ilossless", type=bool, help="Image Lossless", default=True)
        parser.add_argument("-iq", "--iquality", type=int, help="Image Quality", default=100)
        parser.add_argument("--vcrf", help="Video CRF", type=int, default=27)
        parser.add_argument("-vs", "--vskip", help="Video Skip", default=False)
        parser.add_argument("-ve", "--vext", help="Video Extension", default="webm")
        parser.add_argument("-vc", "--vcodec", help="Video Codec", default="libvpx-vp9")
        args = parser.parse_args()

        if args.config is not None:
            if os.path.isfile(args.config):
                with open(args.config, "rb") as cfile:
                    config = tomllib.load(cfile)
            else:
                print("Failed to find config. Check `vnrecode -h` to more info")
                exit(255)

        copy_unprocessed = config["FFMPEG"]["CopyUnprocessed"] if args.config else args.u
        force_compress = config["FFMPEG"]["ForceCompress"] if args.config else args.force
        mimic_mode = config["FFMPEG"]["MimicMode"] if args.config else args.mimic
        hide_errors = config["FFMPEG"]["HideErrors"] if args.config else args.silent
        workers = config["FFMPEG"]["Workers"] if args.config else args.jobs
        webp_rgba = config["FFMPEG"]["WebpRGBA"] if args.config else args.webprgba
        audio_ext = config["AUDIO"]["Extension"] if args.config else args.aext
        audio_bitrate = config["AUDIO"]["BitRate"] if args.config else args.abit
        image_downscale = config["IMAGE"]["ResDownScale"] if args.config else args.idown
        image_ext = config["IMAGE"]["Extension"] if args.config else args.iext
        image_fall_ext = config["IMAGE"]["FallBackExtension"] if args.config else args.ifallext
        image_lossless = config["IMAGE"]["Lossless"] if args.config else args.ilossless
        image_quality = config["IMAGE"]["Quality"] if args.config else args.iquality
        video_crf = config["VIDEO"]["CRF"] if args.config else args.vcrf
        video_skip = config["VIDEO"]["SkipVideo"] if args.config else args.vskip
        video_ext = config["VIDEO"]["Extension"] if args.config else args.vext
        video_codec = config["VIDEO"]["Codec"] if args.config else args.vcodec
        source = args.source

        return cls(
            copy_unprocessed, force_compress, mimic_mode, hide_errors, webp_rgba, workers,
            audio_ext, audio_bitrate,
            image_downscale, image_ext, image_fall_ext, image_lossless, image_quality,
            video_crf, video_skip, video_ext, video_codec, source
        )
