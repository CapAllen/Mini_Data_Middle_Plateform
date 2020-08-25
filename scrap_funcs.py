import requests 
from bs4 import BeautifulSoup 
import urllib

import re
import os
import time 
import shutil  
import datetime
import numpy as np
import pandas as pd
import random

##### 西安教育局
url = 'http://edu.xa.gov.cn/xwzx/tzgg/1.html'
base_url = 'http://edu.xa.gov.cn'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
}

def get_page_data(page):
    url = f'http://edu.xa.gov.cn/xwzx/tzgg/{page}.html'
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.content,'html.parser')
    results = []
    for item in soup.find('div',id='content').find_all('article'):
        title = item.find('a')['title'].replace('\\','').replace('/','').replace('\n','')
        article_url = base_url + item.find('a')['href']
        date = item.find('div', class_='detail').find('span').get_text()

        results.append((title,article_url,date))
    return results

def get_article(title,article_url,date):
    errors = []
    res = requests.get(article_url,headers=headers)
    soup = BeautifulSoup(res.content,'html.parser')
    # 文章内容
    article_content = soup.find('div',id='article')
    if date == '':
        date = soup.find('div',class_='m-txt-crm hidden-sm hidden-xs').find_all('span')[0].get_text()
        date = date.split(' ')[0].replace('发布时间：','')
    file_folder = date+'-'+title
    if not os.path.exists(f'./docs/xian_edu/{file_folder}'):
        os.mkdir(f'./docs/xian_edu/{file_folder}')
    
    with open(f'./docs/xian_edu/{file_folder}/{title}.html','w',encoding='utf-8') as f:
        f.write(str(article_content))
        
    #保存附件
    
    # 添加header
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    for add_item in soup.find('div',id='article').find_all('a'):
        try:
            add_url = add_item['href']
            add_title = add_item.get_text()
            if 'http://' not in add_url:

                add_url = base_url + add_url
            if add_title!='':
                urllib.request.urlretrieve(add_url,f'./docs/xian_edu/{file_folder}/{add_title}.{add_url.split(".")[-1]}')
        except:
#             print(article_url,add_url)
            errors.append((article_url,add_url))
            continue
        
    #保存图片
    img_name = 1
    for img_item in soup.find('div',id='article').find_all('img'):
        img_url = img_item['src']
        if 'http://' not in img_url:
            img_url = base_url + img_url
            
        urllib.request.urlretrieve(img_url,f'./docs/xian_edu/{file_folder}/{img_name}.jpg')
        img_name += 1
        
    return date,errors

def xian_edu_scraper(start_date,end_date):
    # 清空文件夹
    if os.path.exists('./docs/xian_edu/'):
        shutil.rmtree('./docs/xian_edu/')  
    
    os.mkdir('./docs/xian_edu/')  

    # 总数据
    all_results = []    
    page = 1
    date = end_date #今日日期
    errors = []
    while date > start_date: # 上次爬取的日期 
        
        results = get_page_data(page)
        date = results[-1][-1]
        all_results += results
        page += 1       
    
    for item in all_results:
        if (item[-1] >= start_date) and (item[-1] <= end_date):            
            try:
                date,error = get_article(item[0],item[1],item[2])
                errors += error
                time.sleep(1)
            except:
                errors += [item[1]]

        
        with open('errors.txt','w',encoding='utf-8') as f:
            f.write(str(errors))
        yield(len(all_results),all_results.index(item)+1)   

## 知乎用户
headers = {
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://www.zhihu.com',
    'referer': 'https://www.zhihu.com/question/290268306',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}


def extract_data(item):
    
    #id
    item_id = item['id']
    # 问题相关
    question = item['target'].get('question')
    
    if question:
        # 问题标题
        question_title = question['title']
        # 问题内容
        question_excerpt = question['excerpt']
        # 问题回答数量
        answer_count = question['answer_count']
        # 问题评论数量
        comment_count = question['comment_count']
        # 问题关注量
        follower_count = question['follower_count']
        # 问题链接
        question_url = question['url']
        # 提问人昵称
        question_author = question['author']['name']
        # 提问人主页
        question_author_url = question['author']['url']
        # 提问时间
        question_timestamp = question['created']
    else:
        question_title = item['target']['title'] if item['target'].get('title') else ''
        question_excerpt = ''
        answer_count = ''
        comment_count = ''
        follower_count = ''
        question_url = item['target']['url'] if item['target'].get('url') else ''
        question_author = ''
        question_author_url = ''
        question_timestamp = ''
    # 回答相关
    # 回答时间
    answer_created_time = item['created_time']
    #回答更新时间
    answer_updated_time = item['target'].get('updated_time','')
    #回答内容
    answer_content = item['target'].get('content','')
    #赞同数量
    answer_voteup_count = item['target'].get('voteup_count','')
    #评论量
    answer_comment_count = item['target'].get('comment_count','')
    #喜欢量
    answer_thanks_count = item['target'].get('thanks_count','')
    # 回答作者
    answer_author = item['target']['author']['name'] if item['target'].get('author') else ''
    answer_author_url = item['target']['author']['url'] if item['target'].get('author') else ''
    # 回答or收藏
    action_text = item['action_text']
    
    df = pd.DataFrame(columns=['id','问题标题','问题内容','回答数量','问题评论量','问题关注量','问题链接','提问者昵称','提问者主页','提问时间',
                              '回答时间','回答更新时间','回答内容','赞同量','评论量','喜欢量','回答作者','回答作者主页','行为类型'])
    
    df.loc[df.shape[0]] = (item_id,question_title,question_excerpt,answer_count,comment_count,follower_count,question_url,question_author,
                           question_author_url,question_timestamp, answer_created_time,answer_updated_time,answer_content,
                           answer_voteup_count,answer_comment_count,answer_thanks_count,answer_author,answer_author_url,action_text)    
    
    return df

def scrap_user_activities(start_url):

    limit_per_page = int(re.findall(r'limit=(\d+)',start_url)[0])
    # 设置MAX COUNT，至多获取最近一万条数据
    MAX_COUNT = int(10000 / limit_per_page)

    # 初始化
    # if os.path.exists(f'./docs/zhihu_user_activities.csv'):
    #     all_df = pd.read_csv(f'./docs/zhihu_user_activities.csv')

    #     with open(f'./docs/zhihu_user_activities_urls.txt') as f:
    #         next_url_lst = eval(f.read())

    #     count = int(all_df.shape[0] / limit_per_page)
    # else:
    all_df = pd.DataFrame()
    next_url_lst = [start_url]
    count = 0
    
    

    flag = False
    
    print('Scraping...')
    
    while count <= MAX_COUNT:
    
        if count % 50 == 0:
            print(f'Page {count+1} is scraping...')

        res = requests.get(next_url_lst[-1],headers=headers)
        data = res.json()

        #最后一页了吗？
        flag = data['paging']['is_end']
        if flag:
            print('End!!!!!!!!!!!!')
            return(count,count)
            break

        #下一页url
        next_url_lst.append(data['paging']['next'])
        # item_lst
        item_lst = data['data']
        # 保存数据
        df = pd.DataFrame()
        for item in item_lst:
            tmp = extract_data(item)
            df = df.append(tmp)
        
        all_df = all_df.append(df)
        
        all_df.to_excel(f'./docs/zhihu/zhihu_user_activities.xlsx',index=False,encoding='utf-8-sig')
        
        # with open(f'./docs/zhihu/zhihu_user_activities_urls.txt','w') as f:
        #     f.write(str(next_url_lst))

        count += 1
        time.sleep(random.randint(2,4))
        yield(np.log10(MAX_COUNT)+4,np.log10(count)+4)

def scrap_user_videos(user_name,user_url):
    urlToken = user_url.split('/')[-1]
    # 检验是否有视频
    res = requests.get(user_url,headers=headers)
    soup = BeautifulSoup(res.content,'html.parser')
    try:
        video_num = soup.find('div',class_='ProfileMain-header').find_all('a')[2].find('span').get_text()
    except IndexError:
        print(user_url)
    video_num = int(video_num)
    
    columns = ['用户名称','urlToken','视频id','标题','封面','描述','时长（s）',
               '高清链接','发布时间','播放量','评论量','点赞量','视频页链接']
    df = pd.DataFrame(columns=columns)
    
    if video_num > 0:
        print('Scraping Homepage Videos...')
        # 先爬取主页的video
        video_url = user_url + '/zvideos'
        res = requests.get(video_url,headers=headers)
        soup = BeautifulSoup(res.content,'html.parser')
        
        script = soup.find('script',id='js-initialData').get_text()
        script = eval(script.replace('false','False').replace('true','True').replace('null','None'))
        video_items = script['initialState']['entities']['zvideos']
        video_items = list(video_items.values())
        
        for item in video_items:
            video_id = item['id']
            # 视频标题
            video_title = item['title']
            # 封面
            video_imageUrl = item['imageUrl']
            # 描述
            video_description = item['description']
            # 视频时长 单位：s
            video_duration = item['video']['duration']
            # 视频高清链接
            highest_hd = list(item['video']['playlist'].keys())[0]
            video_playUrl = item['video']['playlist'][highest_hd]['playUrl']
            # 发布时间
            video_publishedAt = item['publishedAt']
            # 播放量,评论，点赞
            video_playCount,video_commentCount,video_voteupCount = item['playCount'],item['commentCount'],item['voteupCount']
            # 视频页链接
            video_page_url = item['url'].replace('api/v4/zvideos','zvideo')
            
            df.loc[df.shape[0]] = (user_name,urlToken,video_id,video_title,video_imageUrl,video_description,
                                   video_duration,video_playUrl,video_publishedAt,video_playCount,video_commentCount,
                                   video_voteupCount,video_page_url)
            
            
        
        if len(video_items) < video_num:
            print('Scraping More Videos Through API...')
            # 构造api，爬取更多
            video_api = f'https://www.zhihu.com/api/v4/members/{urlToken}/zvideos?offset={len(video_items)}&limit=10'
            next_lst = [video_api]
            
            is_end = False
            while not is_end:
                res = requests.get(next_lst[-1],headers=headers)
                res_json = res.json()            
                
                for item in res_json['data']:
                    try:
                        highest_hd = list(item['video']['playlist'].keys())[0]
                    except KeyError:
                        print(user_url)
                        return
                    df.loc[df.shape[0]] = (user_name,urlToken,item['id'],item['title'],item['image_url'],item['description'],
                                           item['video']['duration'],item['video']['playlist'][highest_hd]['play_url'],
                                           item['published_at'],item['play_count'],item['comment_count'],item['voteup_count'],
                                           item['url'].replace('api/v4/zvideos','zvideo'))
                
                
                # 下一页链接
                next_lst.append(res_json['paging']['next'])
                # 最后一页吗
                is_end = res_json['paging']['is_end']
    
    if len(df) > 0:
        df.to_excel(f'./docs/zhihu/zhihu_user_activities_videos.xlsx',index=False,encoding='utf-8-sig')

def get_user_details(homepage):

    # 清空文件夹
    if os.path.exists('./docs/zhihu/'):
        shutil.rmtree('./docs/zhihu/')  
    
    os.mkdir('./docs/zhihu/')  
    
    def test_dict(dic,key):
        return item[key]['name'] if item.get(key) else ''
    
    urlToken = homepage.split('/')[-1]
    res = requests.get(homepage,headers=headers)
    soup = BeautifulSoup(res.content,'html.parser')
    # 首图.
    try:
        headpic = soup.find('div',class_='Card').find('div',class_='UserCover').find('div')['data-src']
    except:
        headpic = ''
    
    script = soup.find('script',id='js-initialData').get_text()
    script = eval(script.replace('false','False').replace('true','True').replace('null','None'))
    
    # start url
    start_url = script['initialState']['people']['activitiesByUser'][urlToken]['previous']
    
    user_info = script['initialState']['entities']['users'][urlToken]
    # 头像
    avatar = user_info['avatarUrl']
    name = user_info['name']
    headline = user_info['headline']
    # 个人简介
    description = user_info['description']
    # VIP
    is_VIP = user_info['vipInfo']['isVip']
    # 认证情况
    badges = []
    for item in user_info['badgeV2']['detailBadges']:
        badges.append('{}_{}'.format(item['title'] if item.get('title') else '',item['description'] if item.get('description') else ''))
    
    
    followerCount,followingCount,mutualFolloweesCount,answerCount,questionCount = user_info['followerCount'],user_info['followingCount'],user_info['mutualFolloweesCount'],user_info['answerCount'],user_info['questionCount']
    articlesCount,columnsCount,zvideoCount,favoritedCount,voteupCount,thankedCount = user_info['articlesCount'],user_info['columnsCount'],user_info['zvideoCount'],user_info['favoritedCount'], user_info['voteupCount'],user_info['thankedCount'],
    
    # 所在行业
    business = user_info['business']['name']
    
    # 居住地
    locations = []
    for item in user_info['locations']:
        locations.append(item['name'])
        
    # 职业经历
    employments = []
    for item in user_info['employments']:
        employments.append('{}_{}'.format(test_dict(item,'company'),test_dict(item,'job')))
        
    # 教育经历
    educations = []
    for item in user_info['educations']:
        educations.append('{}_{}'.format(test_dict(item,'school'),test_dict(item,'major')))
    
    columns = ['昵称','主页','首图','头像','头条','个人简介','所在行业','居住地','职业经历','教育经历','是否开通VIP','认证情况',
               '粉丝人数','关注人数','互关人数','回答数','提问数',
              '文章数','专栏数','视频数','被收藏数','获赞数','被喜欢数','start_url']
    
    user_info_data = pd.DataFrame(columns=columns)
    user_info_data.loc[0] = (name,homepage,headpic,avatar,headline,description,business,str(locations),str(employments),str(educations),
                             is_VIP,str(badges),followerCount,followingCount,mutualFolloweesCount,answerCount,questionCount,
                             articlesCount,columnsCount,zvideoCount,favoritedCount,voteupCount,thankedCount,start_url)

    user_info_data.to_excel('./docs/zhihu/zhihu_user_info.xlsx',encoding='utf-8-sig',index=False)

    return user_info_data    




                