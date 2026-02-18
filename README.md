# 政策监控推送系统

自动抓取政府网站最新政策，通过AI分析利好行业和公司，推送到企业微信。

## 功能特点

- 自动监控多个政府网站政策更新
- AI智能分析政策利好行业和相关公司
- 利好程度分级（特大利好/大利好/中利好/小利好）
- 企业微信机器人实时推送
- 支持定时自动运行和手动触发

## 监控网站

- 财政部
- 工信部
- 人民银行
- 发改委
- 商务部
- 国务院办公厅

## 环境要求

- Python 3.11+
- Windows / Linux / macOS

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入配置：

```env
DEEPSEEK_API_KEY=your_api_key_here
WECHAT_WEBHOOK_URL=your_webhook_url_here
POLICY_DAYS=5
```

### 3. 运行程序

```bash
python main.py
```

## GitHub Actions 部署

### 1. 配置 Secrets

在GitHub仓库的 **Settings** → **Secrets and variables** → **Actions** 中添加：

- `DEEPSEEK_API_KEY` - DeepSeek API密钥
- `WECHAT_WEBHOOK_URL` - 企业微信机器人Webhook地址

### 2. 运行方式

**定时自动运行**：每天北京时间20:00自动执行

**手动触发**：
1. 进入仓库 **Actions** → **政策监控推送**
2. 点击 **Run workflow**
3. 可选择填写抓取天数（默认5天）
4. 点击 **Run workflow**

## 配置说明

### POLICY_DAYS

抓取近N天的政策，修改方式：

- **本地运行**：修改 `.env` 文件中的 `POLICY_DAYS` 值
- **GitHub Actions**：手动触发时输入天数，或在 Variables 中配置

### MONITOR_SITES

监控的网站列表，可在 `.env` 文件中通过注释来启用/禁用：

```env
MONITOR_SITES=https://gss.mof.gov.cn/gzdt/zhengcefabu/          #财政部
MONITOR_SITES=https://www.miit.gov.cn/zwgk/zcwj/index.html      #工信部
# MONITOR_SITES=https://www.pbc.gov.cn/...    # 注释掉即可禁用
```

## 推送消息示例

```
【新政策提醒】

政策名称：商务部公告2026年第9号 公布对原产于欧盟的进口相关乳制品反补贴调查的最终裁定

受益行业：国内乳制品行业

利好等级：中利好

判断理由：政策力度：商务部部委级贸易救济措施；市场规模：中国乳制品市场规模数千亿；营收影响：预计国内龙头乳企营收提升约3%-5%

相关公司：伊利股份、蒙牛乳业、光明乳业

政策解读：...

[查看原文](url)
```

## 项目结构

```
ZhengCe/
├── config/
│   ├── .env              # 环境变量（不提交）
│   └── config.py         # 配置加载
├── modules/
│   ├── deepseek_analyzer.py   # AI分析
│   ├── wechat_notifier.py     # 企微推送
│   └── date_filter.py        # 日期过滤
├── scrapers/
│   ├── base_scraper.py    # 基础爬虫
│   ├── mof_scraper.py     # 财政部
│   ├── miit_scraper.py    # 工信部
│   ├── pb_scraper.py      # 人民银行
│   ├── ndrc_scraper.py    # 发改委
│   ├── mofcom_scraper.py  # 商务部
│   └── gov_scraper.py     # 国务院
├── .github/workflows/
│   └── policy_monitor.yml # GitHub Actions配置
├── main.py               # 主程序
└── requirements.txt      # 依赖
```

## 免责声明

本项目仅供学习交流使用，请遵守相关网站的使用条款和政策。
