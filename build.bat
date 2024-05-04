@Echo off
if not defined VIRTUAL_ENV goto :venv_error

mkdir output
mkdir output\bin
python -m pip install -r FFMpeg-Compressor\requirements.txt || goto :exit
python -m pip install -r RenPy-Android-Unpack\requirements.txt || goto :exit
python -m pip install Nuitka || goto :exit
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=ffmpeg-comp FFMpeg-Compressor\main.py || goto :exit
xcopy FFMpeg-Compressor\ffmpeg-comp.toml output\bin /Y
move /Y output\ffmpeg-comp.exe output\bin
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=rendroid-unpack RenPy-Android-Unpack\unpack.py || goto :exit
move /Y output\rendroid-unpack.exe output\bin
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=vnds2renpy VNDS-to-RenPy/convert.py || goto :exit
move /Y output\vnds2renpy.exe output\bin

:venv_error
echo "Please create and activate venv before running this script: python -m venv .\venv && .\venv\Scripts\activate.bat"
goto :exit

:exit
pause
exit /b %exitlevel%