@echo off
chcp 65001 >nul
echo ========================================
echo 删除视频文件以减小代码包大小
echo ========================================
echo.

set VIDEO_DIR=images\coupon\video

if exist "%VIDEO_DIR%" (
    echo 正在删除视频文件...
    del /q "%VIDEO_DIR%\*.mp4" 2>nul
    if %errorlevel% equ 0 (
        echo ✅ 视频文件已删除
    ) else (
        echo ⚠️ 删除失败，请手动删除 %VIDEO_DIR% 目录下的 .mp4 文件
    )
) else (
    echo ℹ️ 视频目录不存在，可能已经删除
)

echo.
echo ========================================
echo 操作完成！
echo ========================================
echo.
echo 提示：
echo 1. 如果视频需要保留，请上传到服务器或云存储
echo 2. 然后更新 pages/index/index.js 中的视频URL
echo 3. 重新编译小程序
echo.
pause

