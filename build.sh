#!/bin/bash
mkdir output
mkdir output/bin
nuitka3 --jobs=$(nproc) --output-dir=output --follow-imports --output-filename=output/bin/ffmpeg-comp FFMpeg-Compressor/main.py
cp FFMpeg-Compressor/ffmpeg-comp.toml output/bin/
nuitka3 --jobs=$(nproc) --output-dir=output --follow-imports --output-filename=output/bin/rendroid-unpack RenPy-Android-Unpack/unpack.py