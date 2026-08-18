"""
Day 2 任务1：并发抓取全部 10 页

把昨天的 fetch_page 和 parse_page 复制过来，
用 asyncio.gather 并发抓取 start=0, 25, 50 ... 225 共 10 页。
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


# TODO: 复制昨天的 fetch_page 和 parse_page
async def fetch_page(session, start):
    url = f"https://movie.douban.com/top250?start={start}"
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 200:
            return await response.text()
        else:
            print(f"请求失败，状态码：{response.status}")
            return None


def parse_page(html):
    movies = []
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all("div", class_="item"):
        rank = item.find('em').text
        title = item.find('span', class_='title').text          # 第一个 title = 中文名
        score = item.find('span', class_='rating_num').text

        # 新结构：评价人数是含"人评价"字样的 span
        bd = item.find('div', class_='bd')
        votes_span = bd.find('span', string=lambda s: s and '人评价' in s)
        votes = int(votes_span.text.replace('人评价', '').replace(',', '')) if votes_span else 0

        # 新结构：简介在 p.quote 里
        quote_tag = bd.find('p', class_='quote')
        quote = quote_tag.text.strip() if quote_tag else None

        url = item.find('a')['href']
        movies.append({
            'rank': int(rank),
            'title': title,
            'score': float(score),
            'votes': votes,
            'quote': quote,
            'url': url
        })
    return movies   # ← 必须在 for 循环外面！


# TODO: crawl_all() 协程：
#   1. starts = [0, 25, 50, ..., 225]（10页）
#   2. asyncio.gather(*(fetch_and_parse(session, s) for s in starts))
#   3. 合并所有页的电影到一个列表
#   4. 打印总数量和前3条
async def fetch_and_parse_page(session, start, sem):
    async with sem:
        html = await fetch_page(session, start)
        if html :
            return parse_page(html)
        return []
async def crawl_all():
    starts = list(range(0,250,25))
    sem = asyncio.Semaphore(3)
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch_and_parse_page(session, start, sem) for start in starts
        ]
        results =await asyncio.gather(*tasks)
        all_movies = []
        for movies in results:
            all_movies.extend(movies)
    for movie in all_movies[:3]:
        print(f"排名：{movie['rank']}")
        print(f"标题：{movie['title']}")
        print(f"评分：{movie['score']}")
        print(f"评价人数：{movie['votes']:,}")
        print(f"简介：{movie['quote']}")
        print("-" * 30)
    return all_movies



# TODO: 限速：豆瓣反爬，10 个并发可能被封 IP
#   提示：asyncio.Semaphore(3) —— 同时最多 3 个请求
#   async with sem: 包裹请求部分


if __name__ == "__main__":
    asyncio.run(crawl_all())
