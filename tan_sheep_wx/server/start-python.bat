@echo off
echo ====================================
echo Python 静态服务器启动脚本
echo ====================================
echo.

REM 检查 Python 是否安装
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到 Python，请先安装 Python
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 检测到 Python
python --version
echo.

REM 检查 images 目录是否存在
if not exist "images" (
    echo [警告] images 目录不存在，正在创建...
    mkdir images
    echo [提示] 请将图片文件放到 server/images/ 目录下
    echo.
)

echo [信息] 正在启动服务器（端口 5001）...
echo [提示] 按 Ctrl+C 可以停止服务器
echo [访问] http://localhost:5001/images/
echo.

REM Python 3.x
python -m http.server 5001

REM 如果是 Python 2.x，使用下面这行：
REM python -m SimpleHTTPServer 5001

pause

