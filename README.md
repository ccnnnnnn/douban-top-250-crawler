# 豆瓣电影 Top250 异步爬虫

> 暑假项目一：异步爬虫 + 数据入库
> 技术栈：asyncio + aiohttp + Pydantic + PostgreSQL

## 目标

- [ ] 异步并发爬取豆瓣电影 Top250（10页 × 25部 = 250部）
- [ ] Pydantic 数据校验
- [ ] 异步写入 PostgreSQL
- [ ] SQL 数据分析（窗口函数）
- [ ] 推送 GitHub

## 文件结构

```
phase6-crawler/
├── config.py          # 配置（URL、并发数、数据库连接）
├── models.py          # Pydantic 数据模型
├── crawler.py         # 爬虫主逻辑（aiohttp + 解析）
├── db.py              # 数据库写入（asyncpg）
├── main.py            # 入口
└── analysis.sql       # 数据分析 SQL
```

## 运行

```bash
pip install aiohttp pydantic asyncpg beautifulsoup4
python main.py
```
