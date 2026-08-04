# Blog Project Memory

## 项目信息
- 博客名: Jone Chow's Blog
- 用户: Jone Chow (GitHub: zzyIyzz)
- 仓库: https://github.com/zzyIyzz/blog-abt-zzylyzz
- 线上地址: https://zzyIyzz.github.io/blog-abt-zzylyzz/
- 技术栈: Hugo + PaperMod (自定义覆盖) + GitHub Pages + GitHub Actions

## 环境
- Hugo v0.147.9 安装在 $env:USERPROFILE\bin\hugo.exe
- Git 代理: 127.0.0.1:7890 (Clash)
- 工作目录: c:\Users\zzzaa\Desktop\blog

## 设计风格
- 极简黑白灰三色 (#000 #fff #888)
- 等宽字体用于导航/日期/标签/代码
- 无圆角、无阴影、无动画、无渐变
- 自定义 layouts/ 完全覆盖 PaperMod 模板

## 管理工具
- start.ps1: PowerShell 管理脚本 (UTF-8 BOM 编码)
- 启动博客.bat: 双击运行包装
- 桌面快捷方式: Shaun博客.lnk

## 注意事项
- PowerShell 5.x 读取 .ps1 需要 UTF-8 BOM 编码
- git push 偶尔 SSL 握手失败，加 -c http.sslVerify=false 可绕过
- hugo 不在 PATH 中，需用完整路径或重启终端
