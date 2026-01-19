# 检查小程序代码包中的大文件
# 用于找出导致代码包过大的文件

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "小程序代码包大小分析工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置工作目录
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

# 排除的目录
$excludeDirs = @("node_modules", ".git", "miniprogram_npm", "__pycache__", ".vscode", ".idea")

# 查找所有文件并计算大小
Write-Host "正在扫描文件..." -ForegroundColor Yellow
$allFiles = Get-ChildItem -Recurse -File | Where-Object {
    $excluded = $false
    foreach ($excludeDir in $excludeDirs) {
        if ($_.FullName -like "*\$excludeDir\*") {
            $excluded = $true
            break
        }
    }
    -not $excluded
}

# 按文件大小排序
$largeFiles = $allFiles | Sort-Object Length -Descending | Select-Object -First 50

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "前50个大文件：" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$totalSize = 0
$index = 1

foreach ($file in $largeFiles) {
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\")
    
    $totalSize += $file.Length
    
    if ($file.Length -gt 100KB) {
        Write-Host "$index. " -NoNewline -ForegroundColor Yellow
        Write-Host "$relativePath" -ForegroundColor White
        Write-Host "   大小: " -NoNewline -ForegroundColor Gray
        if ($sizeMB -gt 1) {
            Write-Host "$sizeMB MB" -ForegroundColor Red
        } elseif ($sizeKB -gt 100) {
            Write-Host "$sizeKB KB" -ForegroundColor Yellow
        } else {
            Write-Host "$sizeKB KB" -ForegroundColor Green
        }
        $index++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "文件类型统计：" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 按文件类型统计
$fileTypes = $allFiles | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 20

foreach ($type in $fileTypes) {
    $typeSize = ($type.Group | Measure-Object -Property Length -Sum).Sum
    $typeSizeKB = [math]::Round($typeSize / 1KB, 2)
    $typeSizeMB = [math]::Round($typeSize / 1MB, 2)
    
    $ext = if ($type.Name) { $type.Name } else { "无扩展名" }
    
    Write-Host "$ext : " -NoNewline -ForegroundColor Cyan
    Write-Host "$($type.Count) 个文件, " -NoNewline -ForegroundColor White
    if ($typeSizeMB -gt 1) {
        Write-Host "$typeSizeMB MB" -ForegroundColor Red
    } else {
        Write-Host "$typeSizeKB KB" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "总大小统计：" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
$totalSizeKB = [math]::Round($totalSize / 1KB, 2)

Write-Host "总文件数: " -NoNewline -ForegroundColor Cyan
Write-Host "$($allFiles.Count)" -ForegroundColor White

Write-Host "总大小: " -NoNewline -ForegroundColor Cyan
if ($totalSizeMB -gt 1) {
    Write-Host "$totalSizeMB MB" -ForegroundColor Red
} else {
    Write-Host "$totalSizeKB KB" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "主包限制: 2 MB" -ForegroundColor Green
Write-Host "当前大小: $totalSizeMB MB" -ForegroundColor $(if ($totalSizeMB -gt 2) { "Red" } else { "Green" })

if ($totalSizeMB -gt 2) {
    Write-Host ""
    Write-Host "⚠️  警告：代码包大小超过限制！" -ForegroundColor Red
    Write-Host ""
    Write-Host "建议操作：" -ForegroundColor Yellow
    Write-Host "1. 删除或压缩大文件（> 100KB）" -ForegroundColor White
    Write-Host "2. 将大图片上传到服务器，使用网络URL" -ForegroundColor White
    Write-Host "3. 删除未使用的资源文件" -ForegroundColor White
    Write-Host "4. 使用分包加载非核心页面" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

