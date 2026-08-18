"""
Day 1 任务：抓取第一页
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


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


async def main():
    connector = aiohttp.TCPConnector(ssl=False)
    # ← connector 要传给 ClientSession，而不是在 session.get 里写 ssl=False
    async with aiohttp.ClientSession(connector=connector) as session:
        html = await fetch_page(session, 0)
        if html:
            movies = parse_page(html)
            print(f"共解析出 {len(movies)} 部电影\n")
            for movie in movies[:5]:
                print(f"排名：{movie['rank']}")
                print(f"标题：{movie['title']}")
                print(f"评分：{movie['score']}")
                print(f"评价人数：{movie['votes']}")
                print(f"简介：{movie['quote']}")
                print(f"链接：{movie['url']}")
                print()


if __name__ == "__main__":
    asyncio.run(main())
