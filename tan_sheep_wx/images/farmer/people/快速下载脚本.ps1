# 养殖户头像图片快速下载脚本
# 使用方法：在 PowerShell 中执行此脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "开始下载养殖户头像图片" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 确保在正确的目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 图片URL模板（使用不同颜色）
$colors = @(
    "4CAF50",  # 绿色
    "2196F3",  # 蓝色
    "FF9800",  # 橙色
    "9C27B0",  # 紫色
    "F44336",  # 红色
    "00BCD4",  # 青色
    "8BC34A",  # 浅绿色
    "FF5722",  # 深橙色
    "3F51B5",  # 靛蓝色
    "E91E63"   # 粉红色
)

# 下载10张图片
for ($i = 1; $i -le 10; $i++) {
    $colorIndex = ($i - 1) % $colors.Length
    $color = $colors[$colorIndex]
    $url = "https://ui-avatars.com/api/?name=Farmer$i&size=200&background=$color&color=fff&bold=true"
    $fileName = "p$i.png"
    
    try {
        Write-Host "正在下载 $fileName..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $url -OutFile $fileName -UseBasicParsing
        Write-Host "  ✓ 已下载 $fileName" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ 下载失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "下载完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "已下载的文件：" -ForegroundColor Cyan
Get-ChildItem -Filter "p*.png" | ForEach-Object {
    Write-Host "  - $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)" -ForegroundColor White
}

