#!/bin/bash
mkdir output
mkdir output/bin
python3 -m pip install Nuitka
case "$(uname -s)" in
    Linux*)     jobs="--jobs=$(nproc)";;
    Darwin*)    jobs="--jobs=$(sysctl -n hw.ncpu)";;
esac
nuitka3 "${jobs}" --output-dir=output --follow-imports --output-filename=output/bin/ffmpeg-comp FFMpeg-Compressor/main.py
cp FFMpeg-Compressor/ffmpeg-comp.toml output/bin/
nuitka3 "${jobs}" --output-dir=output --follow-imports --output-filename=output/bin/rendroid-unpack RenPy-Android-Unpack/unpack.py