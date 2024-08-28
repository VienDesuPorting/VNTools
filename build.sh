#!/usr/bin/env bash
set -e
if [[ "$VIRTUAL_ENV" == "" ]]
then
  echo -e "Please create and activate venv before running this script: \033[100mpython3 -m venv venv && source ./venv/bin/activate\033[49m"
  exit
fi

mkdir -p output
mkdir -p output/bin
python3 -m pip install -r requirements.txt
python3 -m pip install Nuitka
case "$(uname -s)" in
    Linux*)     jobs="--jobs=$(nproc)";;
    Darwin*)    jobs="--jobs=$(sysctl -n hw.ncpu)";;
esac
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=vnrecode vnrecode/__main__.py
cp vnrecode/vnrecode.toml output/bin
mv output/vnrecode output/bin
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=unrenapk unrenapk/__main__.py
mv output/unrenapk output/bin
python3 -m nuitka "${jobs}" --output-dir=output --onefile --follow-imports --output-filename=vnds2renpy vnds2renpy/__main__.py
mv output/vnds2renpy output/bin
echo "Done! You can get binaries into output/bin directory"