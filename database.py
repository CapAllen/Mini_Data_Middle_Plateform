import pymysql
import config
import pandas as pd

# connect mysql
con = pymysql.connect(
    host=config.HOST,
    user=config.USER,
    password=config.PW,
    database=config.DB)

# 筛选数据，并返回
def query_data(form_dict):

