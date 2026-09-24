@echo off
setlocal
py -m pip install -r requirements.txt
py -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name DisplayTune DisplayTune.py
 echo.
echo Build complete: dist\DisplayTune.exe
pause
