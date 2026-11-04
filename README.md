# 抖音评论助手 · 本机 Chrome

一个可安装、可修改、可分发的 **Codex Skill / Agent Plugin**。让智能体在使用者自己的 Chrome 中展开并读取抖音单条视频评论，分别统计一级评论和楼中楼，去重导出 Markdown、JSON，并可归纳质疑、疑问、使用经验和产品建议。

**MIT 许可 · Python 标准库 · 无 API Key · 无采集服务器**

[GitHub 源码](https://github.com/dxl13735922117-eng/douyin-comments-local) · [下载 ZIP](https://github.com/dxl13735922117-eng/douyin-comments-local/archive/refs/heads/main.zip)

English: A local-Chrome workflow skill for reading visible comments and expanded replies on a single Douyin video. Includes a dependency-free Python exporter and installer. A compatible host with local browser-control tools and the user's own signed-in session is required. This is not a standalone crawler.

## 先确认适用环境

| 条件 | 要求 |
|---|---|
| 智能体宿主 | 能加载 `SKILL.md`，并在当前会话提供本机 Chrome 的页面读取、点击、滚动能力 |
| 浏览器 | 使用者自己的 Chrome，已安装并连接宿主的浏览器扩展；能实际读取正文 |
| 登录 | 使用者自行登录抖音，登录/验证码由使用者处理 |
| 本地导出 | Python **3.9+**，仅标准库，无需 pip install |
| 操作系统 | 安装器和导出器按跨平台编写；浏览器控制是否可用由宿主决定。真实流程只在 Windows + 本机 Chrome 环境验证过 |

**安装 skill 不等于获得浏览器控制能力。** 普通网页聊天、未提供浏览器工具的 CLI、云浏览器登录态，都不能自动使用这条本机 Chrome 路线。首次连接仍需使用者安装扩展并授权。

## 三步使用

### 1. 安装

解压本仓库的完整 ZIP，在解压目录运行：

```sh
python install.py
```

有 Git 时也可：

```sh
git clone https://github.com/dxl13735922117-eng/douyin-comments-local.git
cd douyin-comments-local
python install.py
```

Windows 若 `python` 只是 Microsoft Store 别名，可使用已安装的 `py -3 install.py` 或真实 Python 解释器路径；macOS/Linux 常用 `python3 install.py`。

默认只复制 `skills/douyin-comments-local` 到 `~/.agents/skills/douyin-comments-local`，不改浏览器、宿主设置或其他 skill。已有同名目录会停止，绝不合并覆盖。可先预览：

```sh
python install.py --dry-run
```

需要项目安装或兼容宿主的旧技能目录时显式指定父目录：

```sh
python install.py --destination .agents/skills
```

也可直接手动复制整个 `skills/douyin-comments-local` 文件夹。若宿主未自动发现，重启宿主。现行 Codex 目录规则见 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。不要在多个扫描目录重复安装同名 skill。

### 2. 连接自己的 Chrome

按宿主的设置连接本机 Chrome，登录抖音；Codex/ChatGPT 桌面端可参考 [官方浏览器扩展说明](https://learn.chatgpt.com/docs/chrome-extension)。Skill 会先发现工具并核对页面可读性，不要求复制 Cookie 或填写 API Key。

### 3. 发给智能体

```text
使用 $douyin-comments-local 读取这条抖音视频的评论区：粘贴你的视频链接
包含页面可展开的楼中楼，去重导出 Markdown 和 JSON。
按“质疑、疑问、使用经验、产品建议”归类，总结观众最关心的问题，并说明实际读取范围。
```

支持 `/video/视频ID` 完整链接、带 `modal_id` 的链接和 `v.douyin.com` 短链。自然语言给出单条视频链接并说“抓评论”“看评论区”也可触发。

## 会得到什么

```text
本次运行目录/
├── raw/dom_0001.json ...      分批 DOM 读取记录
├── comments_top.json         去重后的一级评论
├── comments_replies.json     去重后的回复，含 parent_cid
├── capture_summary.json      数量、停止原因、完整性限制
├── 评论全文.md               按可读点赞数排序，回复归于父楼
└── 评论分析报告.md 等        用户要求分析时由智能体生成
```

分类允许多标签，产品建议与分析者推导分开，保留相反体验和歧义。分析不调用额外付费 API；由运行此 skill 的智能体完成。

## 本地自检与开发验证

在仓库根目录：

```sh
python skills/douyin-comments-local/scripts/doctor.py
python -m unittest discover -s tests -v
```

`doctor.py` 只检查 Python 和包文件，不接触浏览器和账号。测试使用虚构数据，不把示例当作采集成功；DOM 提取测试需开发者本机已有 Node.js 18+，无第三方 npm 依赖。使用者正常运行 skill 不需要 Node.js。

当前路线在 2026-11-04 的一次真实视频页面读取中取得一级 100 条、回复 75 条，页面显示 207；已读到当前列表底部并展开所有可见入口，不能据此承诺平台全量。新分发代码的验证记录见 [VALIDATION.md](VALIDATION.md)。为保护使用者和评论者，发布包不含该次原始数据、昵称列表或机器路径。

## 插件分发

本仓库还带根 `plugin.json` 和 `.codex-plugin/plugin.json` 兼容清单；技能统一位于 `skills/`。可作为 GitHub 公开仓库发布，也可按 [OpenAI 官方插件打包文档](https://developers.openai.com/plugins/build/plugins) 接入支持的插件分发流程。

直接运行安装器即可安装单个 skill；有清单不等于已上架任何插件市场。上架、公开仓库及跨宿主安装需维护者实际发布和验证。无需捆绑虚假的 MCP 地址或浏览器凭据。

## 边界与维护

- 页面读取可能较慢；无法承诺接口爬虫的速度或精确总量。
- 只读取页面加载、可展开的内容；隐藏、删除或未返回的评论无法补足。页面计数与已读计数都如实报告。
- 抖音改版可能使默认选择器失效。先看实际 DOM 再调整配置；零匹配必须报错，不能当成没有评论。
- 原始评论默认留在本地。运行环境、智能体宿主本身的数据处理规则仍适用；本包没有上传或网络请求逻辑。
- 请使用自己的授权会话并遵守目标网站规则。此项目不含登录凭据，不负责绕过登录、验证码或工具权限。
- 不支持整账号批量采集、其他平台或视频下载。

## 来源与许可

本分发版根据本机 Chrome 的真实页面操作经验独立实现，采用 [MIT License](LICENSE)。早期需求受到 [Pluviobyte/douyin-comments](https://github.com/Pluviobyte/douyin-comments) 的单视频评论工作流启发，感谢其思路分享。该参考仓库在核查时未附许可证；本包未打包其请求注入、签名、接收服务、下载或接口导出脚本，也不沿用其“全量抓取”保证。

MIT 许可覆盖本包代码和文档，不授予第三方评论内容、商标或网站服务的权利。欢迎针对真实失败提交精简、脱敏的复现步骤；不要提交 Cookie、令牌或私人评论数据。
