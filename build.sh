#!/usr/bin/env bash
set -e
if [[ "$VIRTUAL_ENV" == "" ]]
then
  echo -e "Please create and activate venv before running this script: \033[100mpython3 -m venv venv && source ./venv/bin/activate\033[49m"
  exit
fi

mkdir -p output
mkdir -p output/bin
python3 -m pip install -r FFMpeg-Compressor/requirements.txt
python3 -m pip install -r RenPy-Android-Unpack/requirements.txt
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
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=vnds2renpy VNDS-to-RenPy/convert.py
mv output/vnds2renpy output/bin