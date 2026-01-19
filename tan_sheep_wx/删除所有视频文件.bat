@echo off
chcp 65001 >nul
echo ========================================
echo 删除所有视频文件
echo ========================================
echo.

set VIDEO_DIR1=images\coupon\video
set VIDEO_DIR2=server\images\coupon\video

echo 正在删除视频文件...
echo.

if exist "%VIDEO_DIR1%" (
    echo 删除 %VIDEO_DIR1% 目录下的视频文件...
    del /q "%VIDEO_DIR1%\*.mp4" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ %VIDEO_DIR1% 目录下的视频文件已删除
    ) else (
        echo ⚠️ 删除失败，请手动检查 %VIDEO_DIR1% 目录
    )
) else (
    echo ℹ️ %VIDEO_DIR1% 目录不存在
)

echo.

if exist "%VIDEO_DIR2%" (
    echo 删除 %VIDEO_DIR2% 目录下的视频文件...
    del /q "%VIDEO_DIR2%\*.mp4" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ %VIDEO_DIR2% 目录下的视频文件已删除
    ) else (
        echo ⚠️ 删除失败，请手动检查 %VIDEO_DIR2% 目录
    )
) else (
    echo ℹ️ %VIDEO_DIR2% 目录不存在
)

echo.
echo ========================================
echo 操作完成！
echo ========================================
echo.
echo 提示：
echo 1. 视频文件已删除（如果存在）
echo 2. 请重新编译小程序
echo 3. 检查代码包大小
echo.
pause

