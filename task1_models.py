"""
Day 1 任务：Pydantic 数据模型

先定义"爬下来的数据长什么样"。
豆瓣电影 Top250 每部电影的信息：
- 排名 rank
- 电影名 title
- 评分 score
- 评价人数 votes
- 简介 quote
- 详情页链接 url
"""

from pydantic import BaseModel
from typing import Optional


# TODO: 定义 Movie 模型
# 字段：rank: int, title: str, score: float, votes: int, quote: Optional[str], url: str
class Movie(BaseModel):
    rank : int
    title : str
    score : float
    votes : int
    quote : Optional[str]
    url : str
    


# 测试：模拟一条爬到的数据，验证模型能正常工作
if __name__ == "__main__":
    # TODO: 用字典创建 Movie，打印出来
    # 测试缺字段、类型错误的情况（Pydantic 会报什么错？）
    movie1 = Movie(
        rank =1,
        title = "肖申克的救赎",
        score = 9.7,
        votes = 2800000,
        quote = "希望让人自由",
        url = "https://movie.douban.com/dubject/1292052"
    )
    print (movie1)
    print(movie1.model_dump())
    try:
        movie2 = Movie(
            rank = 2,
            title = "霸王别姬",
            score = 9.6,
            votes = 2200000,
    
    )
    except Exception as e :
        print('\n缺失字段报错')
        print(e)

    try:
        movie3= Movie(
            rank=3,
            title="阿甘正传",
            score="9.5",
            votes=2000000,
            quoto = "生活就像一盒巧克力",
            url = "https://movie.douban.com/dubject/1292720"

        )
    except Exception as e:
        print('\n类型错误报错')
        print(e)


