#!/bin/bash
mkdir output
mkdir output/bin
python3 -m pip install -r FFMpeg-Compressor/requirements.txt
python3 -m pip install Nuitka
case "$(uname -s)" in
    Linux*)     jobs="--jobs=$(nproc)";;
    Darwin*)    jobs="--jobs=$(sysctl -n hw.ncpu)";;
esac
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=ffmpeg-comp FFMpeg-Compressor/main.py
cp FFMpeg-Compressor/ffmpeg-comp.toml output/bin
mv output/ffmpeg-comp output/bin
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=rendroid-unpack RenPy-Android-Unpack/unpack.py
mv output/rendroid-unpack output/bin