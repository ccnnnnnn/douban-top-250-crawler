"""
Day 2 任务2：写入 PostgreSQL

把爬到的电影数据写入 PostgreSQL 的 movies 表。
用 asyncpg（异步驱动，跟 aiohttp 同体系）。

先建表（在 psql 里执行）：
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    rank INTEGER,
    title VARCHAR(200),
    score REAL,
    votes INTEGER,
    quote TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

import asyncio
import asyncpg
from datetime import datetime



# TODO: save_movies(movies) 协程：
#   1. conn = await asyncpg.connect(user="ccn", database="student_course")
#   2. 批量插入：
#      await conn.executemany(
#          "INSERT INTO movies (rank, title, score, votes, quote, url) VALUES ($1,$2,$3,$4,$5,$6)",
#          [(m["rank"], m["title"], m["score"], m["votes"], m["quote"], m["url"]) for m in movies]
#      )
#   3. 打印成功条数
#   4. await conn.close()
async def save_movies(movies):
    conn = await asyncpg.connect(user='ccn', database='student_course')
    try:
        await conn.executemany(
            # ← SQL 要有 VALUES ($1,$2,...) 占位符！
            'INSERT INTO movies (rank, title, score, votes, quote, url) VALUES ($1,$2,$3,$4,$5,$6)',
            [(m["rank"], m["title"], m["score"], m["votes"], m["quote"], m["url"]) for m in movies]
            )
        print(f"请求失败，状态码：{response.status}")
        print(f"成功写入 {len(movies)} 条数据")
    except Exception as e:
        print(f"写入失败: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    # 测试：造几条假数据先跑通

