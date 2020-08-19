
import os
import re
import json
import redis
import pymysql
import config
import pandas as pd
from xpinyin import Pinyin


# 初始化pinyin
p = Pinyin()

# 数据类型对照字典
dtype_cc_dict = {
    'for_json': {
        '短文本(中文字符少于50)': 'str',
        '长文本': 'str',
        '整数': 'int',
        '小数': 'float'
    },
    'for_sql': {
        '短文本(中文字符少于50)': 'VARCHAR(100)',
        '长文本': 'TEXT',
        '整数': 'INT',
        '小数': 'FLOAT'
    }
}

# read database info
with open('docs/database_info.json', encoding='utf-8') as f:
    database_info = json.load(f)

# connect mysql
con = pymysql.connect(
    host=config.HOST,
    user=config.USER,
    password=config.PW,
    database=config.DB)

# connect redis
pool = redis.ConnectionPool(host=config.REDIS_HOST,
                            port=config.REDIS_PORT, decode_responses=True)
r = redis.Redis(connection_pool=pool)

# 提取中文，转换拼音，拼接返回
def format_string(x):
    # 提取中文
    ch_part = re.findall(r"[\u4e00-\u9fa5]+", x)
    ch_part = '_'.join(ch_part)
    # 转成拼音
    ch_part = p.get_pinyin(ch_part, '_').replace('___', '_')
    # 提取首字母
    ch_part = ''.join([py[0] for py in ch_part.split('_')])
    # 拼接非中文字符
    en_part = re.findall(r"[a-zA-Z0-9]+", x)
    en_part = ''.join(en_part)

    result = en_part + '_' + ch_part if en_part else ch_part
    return result

# 重名检测
def chongming(x,dc,n=1):
    if x in dc:
        x_lst = x.split('__')
        if len(x_lst) == 1:
            new_x = f'{x}__{n}'
            n += 1
            return chongming(new_x,dc,n)
        else:
            new_n = int(x_lst[-1]) + 1
            new_x = f"{''.join(x_lst[:-1])}__{new_n}"
            return chongming(new_x,dc,new_n)
    else:
        return x 

# 筛选数据，并返回
def query_data(form_dict):

    table_name = form_dict['db_name']
    c_c_dict = database_info[table_name]['c_c_dict']
    select_lst = list(c_c_dict.keys())
    where_str = ''

    for col, query in list(form_dict.items())[1:]:
        query = ' ' if not query else query.replace(' ', '')
        # select 部分
        if query[0].upper() == 'X':
            select_lst.remove(col)

        # where 部分
        if query[0].lower() == 'i':
            new_query = [f'"{query_col}"' for query_col in query[2:].replace(
                '，', ',').split(',')]
            where_str = where_str + col + ' IN (' + \
                ','.join(new_query) + ')' + 'AND '
        elif query[0] in ['>', '<', '=', '!', '！']:
            new_query = f'''{query[0].replace('！','!').replace('!','!=')} "{query[1:]}"'''
            where_str = where_str + col + new_query + 'AND '
        else:
            if query in [' ', 'X', 'x']:
                pass
            else:
                raise Exception('输入有误。')

    select_str = ','.join(select_lst)
    where_str = where_str[:-4]

    if where_str:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name} WHERE {where_str}'
    else:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name}'
    result = pd.read_sql(query_str, con=con)

    # 保存筛选后的数据
    # 保存json版本，提供排序用
    result_js = result.drop('id', axis=1)
    total = result_js.shape[0]
    rows = result_js.to_dict(orient='records')
    result_js = {'total': total, 'rows': rows}

    with open('docs/queried_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(result_js))

    # 更改中文列名，提供下载用
    result_ch = result.rename(columns=lambda x: c_c_dict[x])
    result_ch.to_excel('./docs/queried_data.xlsx',
                       index=False, encoding='utf-8')

    return result

# 修改/删除数据
def edit_data(table_name, form_dict, delete_ids):

    c_c_dict = database_info[table_name]['c_c_dict']
    select_lst = list(c_c_dict.keys())

    # 删除数据

    # 删除new的部分
    new_delete_ids = [x.split('&')[0] for x in delete_ids if 'new' in x]
    delete_ids = [x for x in delete_ids if 'new' not in x]

    if delete_ids:
        for delete_id in delete_ids:
            delete_str = f'DELETE FROM gaokao.{table_name} WHERE (id = {delete_id});'
            cursor = con.cursor()
            cursor.execute(delete_str)
            con.commit()
        print('删除成功')

    # 新旧数据
    # 去除select条目
    form_dict = {key: value for key,
                 value in form_dict.items() if 'select' not in key}

    # 去除被select选中的条目
    new = [x for x in list(form_dict.keys())[1:] if 'new' in x]
    old = [x for x in list(form_dict.keys())[1:] if x not in new]
    new = sorted(list(set([x.split('&')[0] for x in new])))
    new = [x for x in new if x not in new_delete_ids]
    old = sorted(list(set([x.split('&')[0] for x in old])))

    # 修改一条旧数据
    def edit_old_data(old_id):
        # 对于old数据
        # 筛选出对应id的数据
        tables = pd.read_sql(
            f'SELECT * FROM gaokao.{table_name} WHERE id={old_id}', con=con)
        # 将其转换为dict
        old_dict = tables.to_dict(orient='records')[0]
        # 新的数据转为dict，然后更新原dict
        new_dict = {key.split('&')[1]: value for key,
                    value in form_dict.items() if old_id in key}
        old_dict.update(new_dict)
        # replace到数据库中
        keys = ','.join(list(old_dict.keys()))
        values = ','.join([f"'{val}'" for val in list(old_dict.values())])
        replace_str = f'REPLACE INTO gaokao.{table_name} ({keys}) VALUES ({values})'
        cursor = con.cursor()
        cursor.execute(replace_str)
        con.commit()

    for old_id in old:
        edit_old_data(old_id)
        print('旧数据处理完成')

    # 对于new数据
    # 获取当前id的最大值
    max_id = pd.read_sql(f'SELECT MAX(id) FROM gaokao.{table_name}', con=con)
    # 直接replace到数据库中
    for new_id in new:
        new_dict = {key.split('&')[2]: value for key,
                    value in form_dict.items() if new_id in key}
        new_dict['id'] = int(max_id.iloc[0, 0]) + 1
        keys = ','.join(list(new_dict.keys()))
        values = ','.join([f"'{val}'" for val in list(new_dict.values())])
        replace_str = f'REPLACE INTO gaokao.{table_name} ({keys}) VALUES ({values})'
        cursor = con.cursor()
        cursor.execute(replace_str)
        con.commit()
        print('新数据处理完成')


# 创建新数据库
def create_data(form_dict):

    # 提取列名和类型
    idx = 0
    col_names = []
    col_dtypes = []
    for key in upload_dict.keys():
        if ('col' in key) and (idx % 2 == 0):
            col_names.append(upload_dict[key])
        elif ('col' in key) and (idx % 2 == 1):
            col_dtypes.append(upload_dict[key])
        else:
            continue
        idx += 1

    # 删除空的列名
    col_names = [col for col in col_names if col.strip()]

    # 构建中英文对照字典
    c_c_dict = {'id': 'id'}
    for col in col_names:
        col_en = format_string(col)
        # 防止重名
        col_en = chongming(col_en,c_c_dict)
        c_c_dict[col_en] = col
    reverse_c_c_dict = {value: key for key, value in c_c_dict.items()}

    # 构建数据类型字典
    dtype_dict = {reverse_c_c_dict[col]: dtype_cc_dict['for_json']
                  [col_dtypes[col_names.index(col)]] for col in col_names}
    dtype_dict.update({'id': 'int'})

    # 构建并更新到database_info.json中
    db_en = format_string(upload_dict['db_name'])
    # 防止重名
    db_en = chongming(db_en,database_info)

    new_db_dict = {db_en: {
        "in_chinese": upload_dict['db_name'],
        "desc": upload_dict['db_desc'],
        "c_c_dict": c_c_dict,
        "dtype_dict": dtype_dict
    }}
    
    database_info.update(new_db_dict)
    with open('docs/database_info.json','w',encoding='utf-8') as f:
        f.write(json.dumps(database_info,ensure_ascii=False))

    # 写入数据库

    new_df = pd.read_excel('docs/upload_file.*')

    
 



