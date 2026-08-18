"""
Day 2 任务3：错误处理 + 重试机制

网络不稳定时请求可能失败。给 fetch_page 加重试：
  失败 → 等 2 秒 → 重试 → 最多 3 次 → 还失败就放弃返回 None
"""

import asyncio
import aiohttp

HEADERS = {"User-Agent": "Mozilla/5.0"}


# TODO: fetch_with_retry(session, url, max_retries=3) 协程
#   for attempt in range(max_retries):
#       try:
#           请求 + 返回
#       except Exception as e:
#           print(f"第{attempt+1}次失败: {e}")
#           if attempt < max_retries - 1:
#               await asyncio.sleep(2)   # 等2秒再试
#           else:
#               return None              # 重试用完，放弃
async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=HEADERS) as response:
                if response.status ==200:
                    return await response.text()
        except Exception as e:
            print(f"第{attempt + 1}次失败： {e}")
            if attempt < max_retries - 1 :
                await asyncio.sleep(2)
                continue
            else:
                return None



# TODO: 对比：
#   没重试 → 网络抖动一次就丢一页数据
#   有重试 → 抖动自动恢复，最多丢"连续失败3次"的页面
async def fetch_page(session, start):
    url = f"https://movie.douban.com/top250?start={start}"
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print(f"请求失败，状态码：{response.status}")
                return await fetch_with_retry(session, url, max_retries=3)
            else:
                return await response.text()
    except Exception as e:
        # 网络异常（超时/连接失败）也走重试
        print(f"请求异常: {e}")
        return await fetch_with_retry(session, url, max_retries=3)
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

if __name__ == "__main__":
    asyncio.run(crawl_all())
