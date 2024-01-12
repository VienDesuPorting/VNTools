@Echo off
mkdir output
mkdir output\bin
python -m pip install -r FFMpeg-Compressor\requirements.txt
python -m pip install Nuitka
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=ffmpeg-comp FFMpeg-Compressor\main.py
xcopy FFMpeg-Compressor\ffmpeg-comp.toml output\bin
move output\ffmpeg-comp.exe output\bin
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=rendroid-unpack RenPy-Android-Unpack\unpack.py
move output\rendroid-unpack.exe output\bin
pause