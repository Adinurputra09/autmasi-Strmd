@echo off
setlocal

echo ==================================================================
echo   Build EXE - Automasi Panel by Adi Nurputra
echo ==================================================================
echo.

REM Pastikan file script ada di folder yang sama dengan .bat ini
if not exist "automasi_storemode_gui.py" (
    echo [!] File automasi_storemode_gui.py tidak ditemukan di folder ini.
    echo     Pastikan build_exe.bat diletakkan satu folder dengan file .py-nya.
    pause
    exit /b 1
)

echo [1/3] Menginstall/memperbarui PyInstaller...
python -m pip install --upgrade pyinstaller --quiet

echo.
echo [2/3] Membuild file EXE (proses ini bisa memakan waktu beberapa menit)...
pyinstaller --noconfirm --onefile --windowed ^
    --name "AutomasiPanel_AdiNurputra" ^
    --collect-all customtkinter ^
    --hidden-import "PIL._tkinter_finder" ^
    automasi_storemode_gui.py

echo.
echo [3/3] Selesai!
echo.
echo File EXE ada di:  dist\AutomasiPanel_AdiNurputra.exe
echo.
echo Catatan:
echo  - Salin file EXE tersebut ke folder mana saja di komputer Windows,
echo    lalu jalankan langsung (double-click), tidak perlu Python terinstall lagi.
echo  - Folder "macro_data" (config, kalibrasi, riwayat, log) akan otomatis
echo    dibuat di sebelah file EXE saat pertama kali dijalankan.
echo  - Kalau Windows Defender/SmartScreen memblokir saat pertama dibuka,
echo    klik "More info" -^> "Run anyway" (wajar untuk exe hasil PyInstaller
echo    yang belum ditandatangani/code-signed).
echo.
pause
