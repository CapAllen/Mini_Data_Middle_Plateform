import re
import os
import json
import datetime
import requests
from retrying import retry
from bs4 import BeautifulSoup

import config





day_3_ago = str(datetime.date.today() -
                datetime.timedelta(days=config.keep_days))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
}


class Basic_Spyder():

    def start_scrap(self, part_url_dict, rule_func):
        result = {}
        for part_name, part_url in part_url_dict.items():
            res = requests.get(part_url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            item_lst = rule_func(soup)
            result[part_name] = item_lst
        
        # 剔除列表为空的子版块
        result = {key:value for key,value in result.items() if len(value)>1}

        return result


# 西安教育局
xa_edu_url_dict = {'教育要闻': 'http://edu.xa.gov.cn/xwzx/jyyw/1.html',
                   '通知公告': 'http://edu.xa.gov.cn/xwzx/tzgg/1.html',
                   '区域动态': 'http://edu.xa.gov.cn/xwzx/qydt/1.html'}

@retry(stop_max_attempt_number=10,wait_random_min=10,wait_random_max=60)
def xa_edu_rule(soup):
    item_lst = []
    base_url = 'http://edu.xa.gov.cn'
    for item in soup.find('div', id='content').find_all('article'):
        item_dict = {}
        post_date = item.find('div', class_='detail').find('span').get_text()
        if post_date < day_3_ago:
            break
        title = item.find('a')['title'].replace(
            '\\', '').replace('/', '').replace('\n', '')
        article_url = base_url + item.find('a')['href']
        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url
        item_lst.append(item_dict)
    return item_lst

# 省教育厅


sjyt_url_dict = {'公示公告': 'http://jyt.shaanxi.gov.cn/news/gsgg/',
                 '教育厅文件': 'http://jyt.shaanxi.gov.cn/news/jiaoyutingwenjian/'}

@retry(stop_max_attempt_number=10,wait_random_min=10,wait_random_max=60)
def sjyt_rule(soup):
    item_lst = []
    for item in soup.find('div', class_='catlist').find_all('li', class_='catlist_li'):
        item_dict = {}
        # date
        post_date = item.find('span').get_text()
        if post_date < day_3_ago:
            break
        title = item.find('a').get_text()
        article_url = item.find('a')['href']

        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url

        item_lst.append(item_dict)
    return item_lst


# 陕西省招生考试信息网
szw_url_dict = {
    '新闻公告': 'http://www.sneac.com/index/xwgg1.htm',
    '普通高考': 'http://www.sneac.com/zkyw/ptgk.htm',
    '高中学业水平考试': 'http://www.sneac.com/zkyw/gzxyspks.htm',
    '中考': 'http://www.sneac.com/zkyw/zk.htm'
}

@retry(stop_max_attempt_number=10,wait_random_min=10,wait_random_max=60)
def szw_rule(soup):
    item_lst = []
    base_url = 'http://www.sneac.com'
    for item in soup.find('div', class_='list-box').find_all('li'):
        item_dict = {}
        post_date = item.find('span').get_text().replace('/', '-')
        if post_date < day_3_ago:
            break
        title = item.find('a').get_text()
        article_url = base_url + item.find('a')['href'][2:]

        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url

        item_lst.append(item_dict)
    return item_lst


# 官方新闻爬虫
basic_spyder = Basic_Spyder()
xa_edu_result = basic_spyder.start_scrap(xa_edu_url_dict, xa_edu_rule)
sjyt_result = basic_spyder.start_scrap(sjyt_url_dict, sjyt_rule)
szw_result = basic_spyder.start_scrap(szw_url_dict, szw_rule)


official_news = {
    '西安市教育局': {
        'homepage': 'http://edu.xa.gov.cn/',
        'favicon': 'http://edu.xa.gov.cn/images/favicon.ico',
        'result': xa_edu_result},
    '陕西省教育厅': {
        'homepage': 'http://jyt.shaanxi.gov.cn/',
        'favicon': 'http://jyt.shaanxi.gov.cn/favicon.ico',
        'result': sjyt_result},
    '陕西招生考试信息网': {
        'homepage': 'https://www.sneac.com/',
        'favicon': 'https://www.sneac.com/images/bitbug_favicon.ico',
        'result': szw_result}
}

with open('docs/official_news.json','w',encoding='utf-8') as f:
    f.write(json.dumps(official_news,ensure_ascii=False))


## 门户新闻
## 华商报
@retry(stop_max_attempt_number=10,wait_random_min=10,wait_random_max=60)
def huashang():
    huashangbao_url = 'http://edu.hsw.cn/'
    response = requests.get(huashangbao_url)
    soup = BeautifulSoup(response.content,'lxml')
    hot = soup.find('div',class_='list fr')

    huashang_result = []
    for item in hot.find_all('a'):
        item_dict = {}
        media_name = '华商报'
        article_url = item['href']
        article_soup = BeautifulSoup(requests.get(article_url).content,'lxml')
        title = article_soup.find('h1').get_text()
        post_date = article_soup.find('span',class_='article-time').get_text().split(' ')[0]
        
        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url
        huashang_result.append(item_dict)

    return ({
    "华商报教育": {
        "homepage": "http://edu.hsw.cn/",
        "favicon": "http://static.hsw.cn/b/assets/i/favicon.png",
        "result": {'今日推荐':huashang_result}}})

# 新浪教育
@retry(stop_max_attempt_number=10,wait_random_min=10,wait_random_max=60)
def xinlang():
    xinlang_url = 'http://edu.sina.com.cn/'
    response = requests.get(xinlang_url)

    soup = BeautifulSoup(response.content,'lxml')

    rank_news = soup.find('div',class_='rank_news').find_all('a')
    rank_commt = soup.find('div',class_='rank_commt').find_all('a')

    def format_date(date):
        year = date.split('年')[0]
        month = date.split('年')[1].split('月')[0]
        day = date.split('年')[1].split('月')[1].split('日')[0]
        return (f'{year}-{month}-{day}')

    def get_title_date(article_url):
        article_soup = BeautifulSoup(requests.get(article_url).content,'lxml')
        try:
            title = article_soup.find('h1').get_text()
            date = format_date(article_soup.find('span',class_='date').get_text())
        except:
            title = article_soup.find('meta',attrs={'property':"og:title"})['content']
            date = article_soup.find('meta',attrs={'property':"article:published_time"})['content'].split('T')[0]
        return (title,date)

    result = {}
    result['新闻排行'] = []
    for item in rank_news:
        item_dict = {}
        article_url = item['href']
        title,post_date = get_title_date(article_url)
        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url
        result['新闻排行'].append(item_dict)

    result['评论排行'] = []
    for item in rank_commt:
        item_dict = {}
        article_url = item['href']
        title,post_date = get_title_date(article_url)
        item_dict['post_date'] = post_date
        item_dict['title'] = title
        item_dict['article_url'] = article_url
        result['评论排行'].append(item_dict)

    return ({
    "新浪教育": {
        "homepage": "http://edu.sina.com.cn/",
        "favicon": "http://edu.sina.com.cn/favicon.ico",
        "result": result}})

menhu_news = huashang()
menhu_news.update(xinlang())

with open('docs/menhu_news.json','w',encoding='utf-8') as f:
    f.write(json.dumps(menhu_news,ensure_ascii=False))