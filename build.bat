@echo off
chcp 65001 > nul
echo ========================================
echo    Сборка системы управления продажами
echo ========================================
echo.

echo Шаг 1: Проверка PyInstaller...
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo PyInstaller не найден. Устанавливаю...
    pip install pyinstaller
)

echo.
echo Шаг 2: Сборка приложения...
echo Это может занять несколько минут...
echo.

pyinstaller --onefile --windowed --name "CarSalesSystem" --clean main.py

echo.
echo ========================================
if exist "dist\CarSalesSystem.exe" (
    echo    СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo.
    echo    Файл находится в папке: dist\
    echo    Имя файла: CarSalesSystem.exe
) else (
    echo    ОШИБКА СБОРКИ!
    echo    Проверьте сообщения выше.
)
echo ========================================
echo.
pause