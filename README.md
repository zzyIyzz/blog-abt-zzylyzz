# Jone Chow's Blog

基于 Hugo + PaperMod 的个人博客。

## 本地预览

```powershell
hugo server -D
```

打开：http://localhost:1313

## 新建文章

```powershell
hugo new posts/2026-08-01-my-note.md
```

编辑生成的 Markdown 文件，把 `draft: true` 改成 `draft: false`，然后写正文。

## 发布

推送到 GitHub 后，`.github/workflows/hugo.yaml` 会自动构建并发布到 GitHub Pages。
