"""
豆瓣电影 Top250 异步爬虫 —— 完整版
"""

import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"第{attempt+1}次失败：{e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                return None


async def fetch_page(session, start):
    url = f"https://movie.douban.com/top250?start={start}"   # ← https 不是 http
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print(f"请求失败，状态码：{response.status}")
                return await fetch_with_retry(session, url)   # ← await 不能省！
            else:
                return await response.text()
    except Exception as e:
        print(f"请求异常：{e}")
        return await fetch_with_retry(session, url)            # ← await 不能省！


def parse_page(html):
    movies = []
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all("div", class_="item"):
        rank = item.find('em').text
        title = item.find('span', class_='title').text
        score = item.find('span', class_='rating_num').text    # ← rating_num 不是 score
        bd = item.find('div', class_='bd')                     # ← div 不是 span，且不要 .text
        votes_span = bd.find('span', string=lambda s: s and '人评价' in s)
        votes = int(votes_span.text.replace('人评价', '').replace(',', '')) if votes_span else 0
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


async def fetch_and_parse_page(session, start, sem):
    async with sem:
        html = await fetch_page(session, start)
        return parse_page(html) if html else []


async def crawl_all():
    starts = list(range(0, 250, 25))    # ← 10页：0,25,...,225（不是 250*25！）
    sem = asyncio.Semaphore(3)
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_and_parse_page(session, start, sem) for start in starts]
        results = await asyncio.gather(*tasks)
        all_movies = []
        for movies in results:
            all_movies.extend(movies)
    return all_movies


async def save_movies(movies):
    conn = await asyncpg.connect(user='ccn', database='student_course')
    try:
        await conn.executemany(                                 # ← executemany 拼写
            'INSERT INTO movies (rank, title, score, votes, quote, url) VALUES ($1, $2, $3, $4, $5, $6)',
            [(m["rank"], m["title"], m["score"], m["votes"], m["quote"], m["url"]) for m in movies]
        )
        print(f"成功写入 {len(movies)} 条数据")
    except Exception as e:
        print(f"写入失败：{e}")
    finally:
        await conn.close()                                      # ← await 不能省！


async def main():
    all_movies = await crawl_all()
    await save_movies(all_movies)

    if all_movies:
        total = len(all_movies)
        max_score = max(m['score'] for m in all_movies)
        avg_score = round(sum(m['score'] for m in all_movies) / total, 2)
        print(f"共爬取 {total} 部电影")
        print(f"最高分 {max_score}")
        print(f"平均分 {avg_score}")


if __name__ == "__main__":
    asyncio.run(main())
