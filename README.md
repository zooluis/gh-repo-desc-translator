# gh-repo-desc-translator

> 把 GitHub 仓库的英文简介翻译成简体中文和繁体中文的小工具。
> A tiny tool that translates GitHub repository descriptions from English into Simplified Chinese (zh-CN) and Traditional Chinese (zh-TW).

## 功能 / Features

- 输入 `owner/repo` 或完整仓库链接，自动抓取仓库简介并翻译
- 一次同时输出**简体中文**与**繁体中文**两种译文
- CLI 版零第三方依赖，仅用 Python 标准库
- 附单文件网页版（`index.html`），浏览器直接打开即可用，也可部署到 GitHub Pages 手机访问

## 用法 / Usage

### 命令行（CLI）

```bash
# 按 owner/repo 翻译
python translate.py facebook/react

# 按完整仓库链接翻译
python translate.py https://github.com/facebook/react

# 直接翻译一段文字（不抓取仓库）
python translate.py --desc "A declarative UI library"

# JSON 输出（方便脚本调用）
python translate.py facebook/react --json
```

示例输出：

```
Original (EN): A declarative, efficient, and flexible JavaScript library for building user interfaces.
简体中文 (zh-CN): 一个用于构建用户界面的声明式、高效且灵活的 JavaScript 库。
繁体中文 (zh-TW): 一個用於構建用戶界面的聲明式、高效且靈活的 JavaScript 庫。
```

### 网页版（Web）

直接用浏览器打开 `index.html`，粘贴仓库地址点击「翻译」即可；也可以部署到 GitHub Pages 后手机访问。

## 翻译服务说明

| 版本 | 翻译接口 | 是否需要 API Key |
| --- | --- | --- |
| CLI（translate.py） | Google 免费翻译端点 | 否（有频率限制，适合日常小量使用） |
| Web（index.html） | MyMemory 免费翻译 API | 否（匿名每日有限额） |

## 目录结构

```
.
├── translate.py   # CLI 工具（Python 3，零依赖）
├── index.html     # 单文件网页版
├── README.md
└── LICENSE
```

## License

MIT
