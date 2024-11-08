@Echo off
if not defined VIRTUAL_ENV goto :venv_error

mkdir output
mkdir output\bin
python -m pip install -r requirements.txt || goto :exit
python -m pip install Nuitka || goto :exit
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=vnrecode vnrecode || goto :exit
xcopy vnrecode\vnrecode.toml output\bin /Y
move /Y output\vnrecode.exe output\bin
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=unrenapk unrenapk || goto :exit
move /Y output\unrenapk.exe output\bin
python -m nuitka --jobs=%NUMBER_OF_PROCESSORS% --output-dir=output --follow-imports --onefile --output-filename=vnds2renpy vnds2renpy || goto :exit
move /Y output\vnds2renpy.exe output\bin
echo "Done! You can get binaries into output\bin directory"

:venv_error
echo "Please create and activate venv before running this script: python -m venv .\venv && .\venv\Scripts\activate.bat"
goto :exit

:exit
pause
exit /b %exitlevel%