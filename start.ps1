# Hugo Blog 快速启动 & 管理脚本
# 用法: .\start.ps1

$ErrorActionPreference = "Stop"
$BlogDir = $PSScriptRoot
$HugoPort = 1313
$HugoVersion = "0.147.9"

# ─ 颜色输出 ──
function Write-Info    { param($m) Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok      { param($m) Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Warn    { param($m) Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err     { param($m) Write-Host "[ERR]  $m" -ForegroundColor Red }

# ── 检查 Hugo ──
function Test-Hugo {
    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $v = & hugo version 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $oldPref
    if ($code -eq 0) {
        Write-Ok "Hugo 已安装: $v"
        return $true
    } else {
        return $false
    }
}

# ── 安装 Hugo ─
function Install-Hugo {
    Write-Info "正在安装 Hugo v$HugoVersion ..."
    $url = "https://github.com/gohugoio/hugo/releases/download/v${HugoVersion}/hugo_extended_${HugoVersion}_windows-amd64.zip"
    $zipPath = "$env:TEMP\hugo.zip"
    $installDir = "$env:USERPROFILE\bin"

    try {
        Write-Info "下载 Hugo ..."
        Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
        Write-Info "解压到 $installDir ..."
        if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir | Out-Null }
        Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
        Remove-Item $zipPath -Force

        # 添加到 PATH (用户级)
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentPath -notlike "*$installDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "User")
            $env:Path += ";$installDir"
        }
        Write-Ok "Hugo 安装完成！路径: $installDir"
        Write-Warn "如果当前终端仍无法识别 hugo，请重启终端。"
    } catch {
        Write-Err "安装失败: $_"
        Write-Info "请手动下载: $url"
    }
}

# ── 启动 Hugo Server ──
function Start-Server {
    Write-Info "启动 Hugo 开发服务器 (端口 $HugoPort) ..."
    Write-Info "按 Ctrl+C 停止服务器"
    Set-Location $BlogDir
    hugo server -D --bind 0.0.0.0 --baseURL "http://localhost:$HugoPort"
}

# ── 新建文章 ──
function New-Post {
    $title = Read-Host "请输入文章标题"
    if (-not $title) { Write-Err "标题不能为空"; return }
    $slug = $title.ToLower() -replace '[^\w\u4e00-\u9fa5]+', '-' -replace '^-|-$', ''
    $date = Get-Date -Format "yyyy-MM-dd"
    $filename = "${date}-${slug}.md"
    $filepath = Join-Path $BlogDir "content\posts\$filename"

    if (Test-Path $filepath) {
        Write-Warn "文件已存在: $filepath"
        return
    }

    hugo new "posts/$filename" 2>$null
    if (-not (Test-Path $filepath)) {
        # 手动创建
        $now = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        $lines = @(
            "---"
            "title: `"$title`""
            "date: ${now}+08:00"
            "draft: true"
            "tags: []"
            "categories: []"
            'description: ""'
            "---"
            ""
            "<!-- more -->"
            ""
        )
        $template = $lines -join "`n"
        Set-Content -Path $filepath -Value $template -Encoding UTF8
    }

    Write-Ok "文章已创建: content\posts\$filename"
    Write-Info "编辑后记得将 draft: true 改为 draft: false"
}

# ── 构建站点 ──
function Build-Site {
    Write-Info "构建站点 ..."
    Set-Location $BlogDir
    hugo --minify
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "构建成功！输出目录: public/"
    } else {
        Write-Err "构建失败"
    }
}

# ── Git 操作 ──
function Git-Pull {
    Write-Info "拉取最新代码 ..."
    Set-Location $BlogDir
    git pull origin main
    if ($LASTEXITCODE -eq 0) { Write-Ok "拉取成功" } else { Write-Err "拉取失败" }
}

function Git-Push {
    $msg = Read-Host "请输入提交信息"
    if (-not $msg) { $msg = "update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
    Set-Location $BlogDir
    git add -A
    git commit -m $msg
    git push origin main
    if ($LASTEXITCODE -eq 0) { Write-Ok "推送成功" } else { Write-Err "推送失败" }
}

# ── 打开浏览器 ──
function Open-Browser {
    Write-Info "打开 http://localhost:$HugoPort ..."
    Start-Process "http://localhost:$HugoPort"
}

# ── 清理 public 目录 ──
function Clean-Public {
    $publicDir = Join-Path $BlogDir "public"
    if (Test-Path $publicDir) {
        Remove-Item -Recurse -Force $publicDir
        Write-Ok "已清理 public/ 目录"
    } else {
        Write-Info "public/ 目录不存在，无需清理"
    }
}

# ── 启动网页编辑器 ──
function Start-Editor {
    $editorPort = 8787
    $running = $false
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:$editorPort/" -UseBasicParsing -TimeoutSec 2
        $running = $true
    } catch { $running = $false }

    if (-not $running) {
        Write-Info "启动网页编辑器 ..."
        Start-Process -FilePath "python" -ArgumentList "editor_server.py" -WindowStyle Hidden -WorkingDirectory $BlogDir
        Start-Sleep -Seconds 2
    }
    Write-Ok "编辑器地址: http://localhost:$editorPort"
    Start-Process "http://localhost:$editorPort"
}

# ── 主菜单 ──
function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "   Hugo Blog 管理面板 - Jone Chow      " -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  [1] 启动开发服务器 (预览)" -ForegroundColor White
    Write-Host "  [2] 新建文章" -ForegroundColor White
    Write-Host "  [3] 构建站点" -ForegroundColor White
    Write-Host "  [4] 打开浏览器预览" -ForegroundColor White
    Write-Host "  [5] Git 拉取" -ForegroundColor White
    Write-Host "  [6] Git 提交并推送" -ForegroundColor White
    Write-Host "  [7] 清理 public 目录" -ForegroundColor White
    Write-Host "  [8] 检查 Hugo 安装" -ForegroundColor White
    Write-Host "  [9] 打开网页编辑器 (写文章)" -ForegroundColor Green
    Write-Host "  [0] 退出" -ForegroundColor White
    Write-Host ""
}

# ── 主循环 ──
while ($true) {
    Show-Menu
    $choice = Read-Host "请选择操作"
    Write-Host ""

    switch ($choice) {
        "1" { Start-Server }
        "2" { New-Post }
        "3" { Build-Site }
        "4" { Open-Browser }
        "5" { Git-Pull }
        "6" { Git-Push }
        "7" { Clean-Public }
        "8" {
            if (Test-Hugo) { Write-Ok "Hugo 正常" }
            else { Write-Warn "Hugo 未安装"; $install = Read-Host "是否自动安装? (y/n)"; if ($install -eq 'y') { Install-Hugo } }
        }
        "9" { Start-Editor }
        "0" { Write-Info "再见！"; break }
        default { Write-Warn "无效选项，请重新选择" }
    }

    if ($choice -ne "0") {
        Write-Host ""
        Read-Host "按回车键返回菜单"
    }
}
