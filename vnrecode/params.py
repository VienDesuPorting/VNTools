from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Self
import tomllib

@dataclass
class Params:

    """
    This dataclass contains all parameters for utility
    """

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

    source: Path
    dest: Path

    @classmethod
    def setup(cls) -> Self:
        """
        Method initialize all parameters and returns class instance
        :return: Params instance
        """
        args = cls.get_args()
        if args.config is not None:
            if Path(args.config).is_file():
                with open(args.config, "rb") as cfile:
                    config = tomllib.load(cfile)
            else:
                print("Failed to find config. Check `vnrecode -h` to more info")
                exit(255)

        copy_unprocessed = config["FFMPEG"]["CopyUnprocessed"] if args.config else args.unproc
        force_compress = config["FFMPEG"]["ForceCompress"] if args.config else args.force
        mimic_mode = config["FFMPEG"]["MimicMode"] if args.config else args.mimic
        hide_errors = config["FFMPEG"]["HideErrors"] if args.config else args.show_errors
        workers = config["FFMPEG"]["Workers"] if args.config else args.jobs
        webp_rgba = config["FFMPEG"]["WebpRGBA"] if args.config else args.webp_rgba
        audio_ext = config["AUDIO"]["Extension"] if args.config else args.a_ext
        audio_bitrate = config["AUDIO"]["BitRate"] if args.config else args.a_bit
        image_downscale = config["IMAGE"]["ResDownScale"] if args.config else args.i_down
        image_ext = config["IMAGE"]["Extension"] if args.config else args.i_ext
        image_fall_ext = config["IMAGE"]["FallBackExtension"] if args.config else args.i_fallext
        image_lossless = config["IMAGE"]["Lossless"] if args.config else args.i_lossless
        image_quality = config["IMAGE"]["Quality"] if args.config else args.i_quality
        video_crf = config["VIDEO"]["CRF"] if args.config else args.v_crf
        video_skip = config["VIDEO"]["SkipVideo"] if args.config else args.v_skip
        video_ext = config["VIDEO"]["Extension"] if args.config else args.v_ext
        video_codec = config["VIDEO"]["Codec"] if args.config else args.v_codec
        source = Path(args.source)
        if not source.exists():
            print("Requested path does not exists. Exiting!")
            exit(255)
        dest = Path(source.parent, source.name + f"_compressed")

        return cls(
            copy_unprocessed, force_compress, mimic_mode, hide_errors, webp_rgba, workers,
            audio_ext, audio_bitrate,
            image_downscale, image_ext, image_fall_ext, image_lossless, image_quality,
            video_crf, video_skip, video_ext, video_codec, source, dest
        )

    @staticmethod
    def get_args() -> Namespace:
        """
        Method gets CLI arguments and returns argparse.Namespace instance
        :return: argparse.Namespace of CLI args
        """
        parser = ArgumentParser(prog="vnrecode",
                                description="Python utility to compress Visual Novel Resources"
                                )
        parser.add_argument("source", help="Directory with game files to recode")
        parser.add_argument("-c", dest='config', help="Utility config file")
        parser.add_argument("-nu", dest='unproc', action='store_false', help="Don't copy unprocessed")
        parser.add_argument("-f", "--force", action='store_true', help="Try to recode unknown files")
        parser.add_argument("-nm", "--no-mimic", dest='mimic', action='store_false', help="Disable mimic mode")
        parser.add_argument("-v", "--show_errors", action='store_false', help="Show recode errors")
        parser.add_argument("--webp-rgb", dest='webp_rgba', action='store_false', help="Recode .webp without alpha channel")
        parser.add_argument("-j", "--jobs", type=int, help="Number of threads (default: 16)", default=16)
        parser.add_argument("-ae", dest="a_ext", help="Audio extension (default: opus)", default="opus")
        parser.add_argument("-ab", dest="a_bit", help="Audio bit rate (default: 128k)", default="128k")
        parser.add_argument("-id", dest="i_down", type=float, help="Image resolution downscale multiplier (default: 1)", default=1)
        parser.add_argument("-ie", dest="i_ext", help="Image extension (default: avif)", default="avif")
        parser.add_argument("-ife", dest="i_fallext", help="Image fallback extension (default: webp)", default="webp")
        parser.add_argument("-il", dest='i_lossless', action='store_false', help="Image losing compression mode")
        parser.add_argument("-iq", dest="i_quality", type=int, help="Image quality (default: 100)", default=100)
        parser.add_argument("--v_crf", help="Video CRF number (default: 27)", type=int, default=27)
        parser.add_argument("-vs", dest="v_skip", action='store_true', help="Skip video recoding")
        parser.add_argument("-ve", dest="v_ext", help="Video extension (default: webm)", default="webm")
        parser.add_argument("-vc", dest="v_codec", help="Video codec name (default: libvpx-vp9)", default="libvpx-vp9")
        args = parser.parse_args()
        return args