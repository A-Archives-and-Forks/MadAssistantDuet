@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 定义ANSI颜色代码
for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "RESET=%ESC%[0m"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "CYAN=%ESC%[36m"
set "WHITE=%ESC%[37m"
set "BOLD=%ESC%[1m"

:: 初始化错误标志
set "ErrorOccurred=0"

:: 获取脚本所在目录（安装包根目录）
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

echo.
echo %BLUE%====================================================================================================%RESET%
echo %BOLD%%CYAN%正在安装 Python 依赖库%RESET%
echo %BOLD%%CYAN%Installing Python Dependencies%RESET%
echo %BLUE%====================================================================================================%RESET%
echo.

:: 检查 Python 是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%错误: 未检测到 Python，请先安装 Python 3.8 或更高版本%RESET%
    echo %RED%Error: Python not detected. Please install Python 3.8 or higher first.%RESET%
    echo.
    echo %YELLOW%您可以从以下链接下载 Python:%RESET%
    echo %YELLOW%You can download Python from:%RESET%
    echo %CYAN%https://www.python.org/downloads/%RESET%
    echo.
    set "ErrorOccurred=1"
    goto :end
)

:: 显示 Python 版本
echo %GREEN%检测到 Python 版本:%RESET%
echo %GREEN%Detected Python version:%RESET%
python --version
echo.

:: 检查 requirements.txt 是否存在
if not exist "requirements.txt" (
    echo %RED%错误: 未找到 requirements.txt 文件%RESET%
    echo %RED%Error: requirements.txt not found%RESET%
    set "ErrorOccurred=1"
    goto :end
)

echo %YELLOW%正在安装依赖包...%RESET%
echo %YELLOW%Installing dependencies...%RESET%
echo.

:: 升级 pip
echo %CYAN%正在升级 pip...%RESET%
echo %CYAN%Upgrading pip...%RESET%
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo %YELLOW%警告: pip 升级失败，但将继续安装依赖%RESET%
    echo %YELLOW%Warning: pip upgrade failed, but will continue with dependency installation%RESET%
)
echo.

:: 安装 requirements.txt 中的依赖
echo %CYAN%正在安装 requirements.txt 中的依赖...%RESET%
echo %CYAN%Installing dependencies from requirements.txt...%RESET%
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %RED%错误: 依赖安装失败%RESET%
    echo %RED%Error: Dependency installation failed%RESET%
    set "ErrorOccurred=1"
    goto :end
)
echo.

:: 运行 pywin32 安装后脚本
echo %BLUE%====================================================================================================%RESET%
echo %BOLD%%CYAN%正在运行 pywin32 安装后脚本%RESET%
echo %BOLD%%CYAN%Running pywin32 post-install script%RESET%
echo %BLUE%====================================================================================================%RESET%
echo.

:: 检查是否具有管理员权限
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%pywin32 安装后脚本需要管理员权限，正在获取权限...%RESET%
    echo %YELLOW%pywin32 post-install script requires administrator privileges, obtaining permissions...%RESET%
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~f0' -Verb RunAs"
    exit /b
)

:: 查找 Python 安装路径中的 pywin32_postinstall.py
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%i"
for %%i in ("%PYTHON_EXE%") do set "PYTHON_DIR=%%~dpi"

:: 尝试查找 pywin32_postinstall.py
set "POSTINSTALL_SCRIPT="
if exist "%PYTHON_DIR%Scripts\pywin32_postinstall.py" (
    set "POSTINSTALL_SCRIPT=%PYTHON_DIR%Scripts\pywin32_postinstall.py"
) else (
    for /f "delims=" %%i in ('python -c "import os, sys; print(os.path.join(sys.prefix, 'Scripts', 'pywin32_postinstall.py'))"') do set "POSTINSTALL_SCRIPT=%%i"
)

if exist "%POSTINSTALL_SCRIPT%" (
    echo %CYAN%找到 pywin32 安装后脚本: %POSTINSTALL_SCRIPT%%RESET%
    echo %CYAN%Found pywin32 post-install script: %POSTINSTALL_SCRIPT%%RESET%
    echo.
    python "%POSTINSTALL_SCRIPT%" -install
    if %errorlevel% neq 0 (
        echo %YELLOW%警告: pywin32 安装后脚本执行失败%RESET%
        echo %YELLOW%Warning: pywin32 post-install script execution failed%RESET%
        set "ErrorOccurred=1"
    ) else (
        echo %GREEN%pywin32 安装后脚本执行成功%RESET%
        echo %GREEN%pywin32 post-install script executed successfully%RESET%
    )
) else (
    echo %YELLOW%警告: 未找到 pywin32 安装后脚本，可能 pywin32 未正确安装%RESET%
    echo %YELLOW%Warning: pywin32 post-install script not found, pywin32 may not be installed correctly%RESET%
    echo.
    echo %YELLOW%尝试手动运行安装后脚本...%RESET%
    echo %YELLOW%Trying to run post-install script manually...%RESET%
    python -c "import win32api; print('pywin32 is installed correctly')" 2>nul
    if %errorlevel% neq 0 (
        set "ErrorOccurred=1"
    )
)
echo.

:end
echo %BLUE%====================================================================================================%RESET%
if %ErrorOccurred% equ 0 (
    echo %BOLD%%GREEN%Python 依赖安装完成！%RESET%
    echo %BOLD%%GREEN%Python dependencies installation completed!%RESET%
) else (
    echo %BOLD%%RED%安装过程中出现错误，请查看上述输出信息%RESET%
    echo %BOLD%%RED%Errors occurred during installation, please check the output above%RESET%
)
echo %BLUE%====================================================================================================%RESET%
echo.

pause
