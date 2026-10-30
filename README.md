# 慢记 · Slow Notes

> 在快世界里，慢慢记录。

一个使用 **Python + Flask + SQLite** 构建的中文个人博客。以暖白、森林绿与陶土橙为主色，结合衬线标题、摄影封面和留白，记录设计、技术与生活。作者：**李文豪**。

## 项目预览

![](./pics/0345.png)


![](./pics/0367.png)

## 功能

- 首页精选与按发布时间排序的文章列表
- 设计灵感、技术手记、生活方式、漫游日记四类内容
- 标题、摘要与正文搜索
- 在线发布文章：必填校验、摘要自动提取、阅读时长估算
- 纯文本正文展示，保留换行与缩进，并对 HTML 转义
- 浏览器本地收藏及状态提示
- SQLite 自动初始化与正文列迁移，保留已有文章
- 十篇初始化文章，包含 Transformer、Python asyncio 和 SQLite 技术内容
- 响应式布局、键盘焦点样式和 404 页面

## QuickStart

需要 Python 3.9 或以上版本。

```bash
git clone https://github.com/Frankie32244/slow-notes.git
cd slow-notes
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
```

macOS / Linux：

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。首次启动自动生成 `blog.sqlite3` 和初始化内容。点击导航的“写博客”或文章栏的“＋ 写博客”即可添加文章。

## 技术栈与目录

| 层级 | 技术 |
| --- | --- |
| 后端 | Python、Flask、Jinja2 |
| 数据存储 | SQLite、参数化 SQL |
| 前端 | HTML、CSS、原生 JavaScript |
| 测试 | unittest、Flask test client |

```text
slow-notes/
├── app.py                 # 路由、数据库初始化、搜索与发布
├── technical_posts.py     # 技术文章初始化内容
├── requirements.txt
├── templates/             # 首页、文章、写作、关于与 404 模板
├── static/                # CSS 样式、收藏交互
├── tests/test_app.py      # 页面、搜索、发布和输入安全验证
└── docs/screenshots/      # 实际网站截图
```

## 测试

在安装依赖的 Python 环境中运行：

```bash
python -m unittest discover -s tests -v
```

目前包含六项测试，覆盖页面访问、分类与搜索、作者及技术内容、空结果、404，以及发布校验、数据保留和 HTML 转义。发布测试使用独立临时数据库。

## 定制与数据

- `templates/about.html`：修改作者介绍。
- `static/style.css`：调整主题色、字体和响应式布局。
- `app.py` 的 `SEEDS` 与 `technical_posts.py`：初始化文章，已存在的 slug 不会被覆盖。
- 旧示例文章使用 `templates/article.html` 中的演示正文；新发布文章使用独立的数据库正文。
- `blog.sqlite3` 保存文章，建议自行备份；数据库、日志和虚拟环境不提交到 GitHub。
- 收藏保存在当前浏览器的 localStorage 中。

## 运行说明

当前版本定位为本机个人博客，写作入口没有登录限制；公开部署前应增加作者认证、持久化会话密钥及生产 WSGI 配置。目前不包含文章编辑、删除或草稿功能。

封面来自 [Unsplash](https://unsplash.com/)，在线字体来自 Google Fonts，需要网络连接；字体加载失败会回退到本机字体。

## 技术文章参考

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Python asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)
