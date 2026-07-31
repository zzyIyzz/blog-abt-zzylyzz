# 学习札记

这是一个 Hugo + PaperMod 搭建的本地学习博客。

## 本地预览

```powershell
hugo server -D
```

打开：

```text
http://localhost:1313
```

如果当前 PowerShell 还识别不了 `hugo`，关闭终端重新打开一次即可。

## 新建文章

```powershell
hugo new posts/2026-06-03-my-note.md
```

编辑生成的 Markdown 文件，把 `draft: true` 改成 `draft: false`，然后写正文。

## 发布

推送到 GitHub 后，`.github/workflows/hugo.yaml` 会自动构建并发布到 GitHub Pages。
