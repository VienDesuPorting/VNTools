from dataclasses import dataclass
from typing import Self


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

    @classmethod
    def setup(cls, config, args) -> Self:
        copy_unprocessed = config["FFMPEG"]["CopyUnprocessed"] if not args.u else args.u
        force_compress = config["FFMPEG"]["ForceCompress"] if not args.force else args.force
        mimic_mode = config["FFMPEG"]["MimicMode"] if not args.mimic else args.mimic
        hide_errors = config["FFMPEG"]["HideErrors"] if not args.silent else args.silent
        workers = config["FFMPEG"]["Workers"] if args.jobs is None else args.jobs
        webp_rgba = config["FFMPEG"]["WebpRGBA"] if not args.webprgba else args.webprgba
        audio_ext = config["AUDIO"]["Extension"] if args.aext is None else args.aext
        audio_bitrate = config["AUDIO"]["BitRate"] if args.abit is None else args.abit
        image_downscale = config["IMAGE"]["ResDownScale"] if args.idown is None else args.idown
        image_ext = config["IMAGE"]["Extension"] if args.iext is None else args.iext
        image_fall_ext = config["IMAGE"]["FallBackExtension"] if args.ifallext is None else args.ifallext
        image_lossless = config["IMAGE"]["Lossless"] if not args.ilossless else args.ilossless
        image_quality = config["IMAGE"]["Quality"] if args.iquality is None else args.iquality
        video_crf = config["VIDEO"]["CRF"] if args.vcrf is None else args.vcrf
        video_skip = config["VIDEO"]["SkipVideo"] if args.vskip is None else args.vskip
        video_ext = config["VIDEO"]["Extension"] if args.vext is None else args.vext
        video_codec = config["VIDEO"]["Codec"] if args.vcodec is None else args.vcodec

        return cls(
            copy_unprocessed, force_compress, mimic_mode, hide_errors, webp_rgba, workers,
            audio_ext, audio_bitrate,
            image_downscale, image_ext, image_fall_ext, image_lossless, image_quality,
            video_crf, video_skip, video_ext, video_codec
        )
