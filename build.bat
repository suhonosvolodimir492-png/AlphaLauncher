@echo off
rem Сборка AlphaLauncher.exe. Запускать из папки AlphaLauncher (двойной клик или cmd).
setlocal
cd /d "%~dp0"

python -m pip install --upgrade pip || goto :error
python -m pip install -r requirements.txt pyinstaller || goto :error

set ICON_ARG=
if exist assets\icon.ico set ICON_ARG=--icon assets\icon.ico

python -m PyInstaller --noconsole --onefile --clean --name AlphaLauncher %ICON_ARG% main.py || goto :error

copy /Y dist\AlphaLauncher.exe AlphaLauncher.exe >nul
echo.
echo Готово: %~dp0AlphaLauncher.exe
echo Папки assets, data и minecraft должны лежать рядом с exe.
pause
exit /b 0

:error
echo.
echo Сборка завершилась с ошибкой. Проверьте вывод выше.
pause
exit /b 1
