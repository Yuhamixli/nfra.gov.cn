@echo off
echo 启动每日更新模式...
echo.

REM 尝试不同的Python命令
if exist "C:\ProgramData\anaconda3\python.exe" (
    echo 使用Anaconda Python...
    "C:\ProgramData\anaconda3\python.exe" main.py daily
) else if exist "C:\Python3\python.exe" (
    echo 使用标准Python安装...
    "C:\Python3\python.exe" main.py daily
) else (
    echo 尝试PATH中的python命令...
    python main.py daily
)

echo.
echo 按任意键退出...
pause 