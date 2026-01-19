@echo off
echo ====================================
echo 本地图片服务器启动脚本
echo ====================================
echo.

REM 检查 Node.js 是否安装
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    echo 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] 检测到 Node.js
node --version
echo.

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo [信息] 首次运行，正在安装依赖...
    call npm install
    echo.
)

REM 检查 images 目录是否存在
if not exist "images" (
    echo [警告] images 目录不存在，正在创建...
    mkdir images
    echo [提示] 请将图片文件放到 server/images/ 目录下
    echo.
)

echo [信息] 正在启动服务器...
echo [提示] 按 Ctrl+C 可以停止服务器
echo.

node server.js

pause

