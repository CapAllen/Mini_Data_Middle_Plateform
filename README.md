# 数据微中台
## 1.项目概览

![wF712R.png](https://s1.ax1x.com/2020/09/04/wF712R.png)

本项目基于Python+Flask+MySQL+Redis搭建，丰富的注释&面向对象方法，可以让你快速上手&个性化拓展，适用于团队内部快速获取信息、分享数据、产出数据产品，无需编程技能，便可实现：

- 首页集成行业新闻动态；

- 数据库管理：
  - 单/多条件数据筛选、模糊筛选；
  - 数据排序、下载；
  - 修改、删除数据；
  - 批量上传，更新数据库；
  - 新建数据库。

- 数据获取：
  - 相关部门公开信息爬虫；
  - 知乎用户动态/问题爬虫；

- ~~拖拽式可视化套件（非开源）~~

- ~~数据产品（非开源）~~



产品截图：

![wF7GKx.gif](https://s1.ax1x.com/2020/09/04/wF7GKx.gif)



## 2.文件组成



```
├── app_run.py ------------------------# 项目主程序
├── config.py -------------------------# 配置文件
├── database.py -----------------------# 数据库操作函数
├── database_helper.py ----------------# 个性化数据库操作函数
├── edu_news.py -----------------------# 首页咨询爬虫
├── scrap_funcs.py --------------------# 知乎等爬虫函数
├── templates/
│   ├── xxx.html-----------------------# 各页面模板
├── static ----------------------------# css及js
├── docs ------------------------------# 中间数据json等
```



## 3.快速启动

1. 配置并打开`redis-server`

2. 依次执行如下代码

   ```
   git clone https://github.com/CapAllen/Mini_Data_Middle_Plateform
   pip install -r requirements.txt
   
   cd Mini_Data_Middle_Plateform
   # 打开config.py文件，配置相关参数
   python app_run.py
   ```

3. 打开浏览器输入http://localhost:8080/



**ENJOY !**

![](https://gitee.com/capallen/files_blocked/raw/master/giphy.webp)



<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt=" Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" style="float:left" /></a>