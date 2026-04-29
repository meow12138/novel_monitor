# Novel Monitor - 海外爆款小说监控系统

全自动抓取海外主流网文平台排行榜数据，监控爆款小说趋势。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy / SQLite |
| 爬虫 | httpx / BeautifulSoup / lxml |
| 调度 | APScheduler |
| 前端 | Vue 3 / Vite / Element Plus / ECharts |

## 已覆盖平台

### 已实现爬虫（可自动抓取）
- **WebNovel** — 阅文海外，全球最大中国网文英译站
- **GoodNovel** — 新阅时代，印尼/泰国市场突出
- **Dreame** — 无限进制，土耳其收入榜第一
- **Royal Road** — 欧美最大奇幻/LitRPG网文社区
- **Wattpad** — 全球最大 UGC 小说社区

### 已录入平台（待开发爬虫）
- Ficool / Bravonovel / BabelNovel / Tapas
- Kakao Page (韩国) / 小説家になろう (日本)
- Amazon Kindle 排行榜

## 快速启动

### 方式一：一键部署到服务器（阿里云 ECS / Windows）

以管理员身份运行 PowerShell：

```powershell
git clone https://github.com/meow12138/novel_monitor.git C:\novel_monitor
cd C:\novel_monitor
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\deploy.ps1
```

或直接双击 `deploy.bat`（需管理员权限）。

部署脚本会自动完成：环境检测 → 依赖安装 → 前端构建 → 注册开机自启 → 启动服务。

### 方式二：本地开发启动

```bash
start.bat
```

### 方式三：手动启动

**后端**
```bash
cd server
pip install -r requirements.txt
python run.py
```

**前端**（开发模式）
```bash
cd web
npm install
npm run dev
```

### 访问地址

| 场景 | 地址 |
|------|------|
| 生产环境（部署后） | http://\<ECS公网IP\>:8001 |
| 本地开发 - 前端 | http://localhost:3000 |
| 本地开发 - 后端 | http://localhost:8001 |
| API 文档 | http://localhost:8001/docs |

> **重要**：部署到阿里云后，需在安全组中放行 TCP 8001 端口。

## 项目结构

```
novel_monitor/
├── server/                  # 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── dashboard.py # 仪表盘
│   │   │   ├── novels.py    # 小说管理
│   │   │   ├── platforms.py # 平台管理
│   │   │   └── tasks.py     # 抓取任务
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 配置
│   │   │   └── database.py  # 数据库
│   │   ├── models/          # 数据模型
│   │   │   └── models.py    # ORM 模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── scrapers/        # 爬虫模块
│   │   │   ├── base.py      # 爬虫基类
│   │   │   ├── registry.py  # 爬虫注册表
│   │   │   ├── webnovel.py
│   │   │   ├── goodnovel.py
│   │   │   ├── dreame.py
│   │   │   ├── royalroad.py
│   │   │   └── wattpad.py
│   │   ├── services/        # 业务逻辑
│   │   │   ├── scrape_service.py
│   │   │   ├── scheduler.py
│   │   │   └── seed.py
│   │   └── main.py          # 应用入口
│   ├── requirements.txt
│   └── run.py
├── web/                     # 前端
│   ├── src/
│   │   ├── api/             # API 调用
│   │   ├── router/          # 路由
│   │   ├── views/           # 页面
│   │   │   ├── Dashboard.vue
│   │   │   ├── Ranking.vue
│   │   │   ├── Novels.vue
│   │   │   ├── NovelDetail.vue
│   │   │   ├── Platforms.vue
│   │   │   └── Tasks.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── start.bat
└── README.md
```

## 功能说明

### 仪表盘
- 小说总数、平台数、今日抓取量统计
- TOP 10 热门小说
- 最近抓取任务时间线

### 排行榜
- 按平台筛选
- 支持热门榜/趋势榜/新书榜/完结榜
- 按评分/阅读量/收藏排序

### 小说管理
- 多条件搜索（书名、作者、平台、类型）
- 小说详情页含数据趋势图（ECharts）
- 直达原文链接

### 平台管理
- 平台启用/停用
- 单平台抓取 / 一键全部抓取
- 爬虫实现状态展示

### 抓取任务
- 任务状态追踪（成功/失败/运行中）
- 任务耗时统计

### 定时调度
- 默认每 60 分钟自动抓取一次
- 可通过环境变量 `SCRAPE_INTERVAL_MINUTES` 调整

## 扩展新平台

1. 在 `server/app/scrapers/` 下新建爬虫文件
2. 继承 `BaseScraper`，实现 `scrape_ranking` 方法
3. 在 `registry.py` 中注册
4. 在 `DEFAULT_PLATFORMS` 中添加平台信息
