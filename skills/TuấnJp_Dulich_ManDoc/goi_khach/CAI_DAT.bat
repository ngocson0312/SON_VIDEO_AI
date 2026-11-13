@echo off
rem Cai thu vien Python + kiem may cho skill TuanJp_Dulich_ManDoc. Them --tai-mo-hinh de tai san Whisper (~3 GB).
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set "SK="
for /d %%D in (".claude\skills\Tu*Dulich_ManDoc") do set "SK=%%D"
if not defined SK (
  echo [!] Khong thay thu muc .claude\skills\TuanJp_Dulich_ManDoc - giai nen lai day du goi zip.
  pause
  exit /b 1
)
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  echo [!] Chua co Python. Cai Python 3.10+ tu python.org ^(tick "Add python.exe to PATH"^) hoac: winget install Python.Python.3.12
  echo     Cai xong mo lai cua so va chay lai CAI_DAT.bat
  pause
  exit /b 1
)
%PY% -I -X utf8 "%SK%\scripts\run.py" cai-dat %*
echo.
pause
