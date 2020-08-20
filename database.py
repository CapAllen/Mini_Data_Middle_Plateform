
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
                            port=config.REDIS_PORT, 
                            password=config.REDIS_PW,
                            decode_responses=True)
r = redis.Redis(connection_pool=pool)

# 提取中文，转换拼音，拼接返回
def format_string(x):
    # 提取中文
    ch_part = re.findall(r"[\u4e00-\u9fa5]+", x)
    ch_part = '_'.join(ch_part)
    if ch_part:
        # 转成拼音
        ch_part = p.get_pinyin(ch_part, '_').replace('___', '_')
        # 提取首字母
        ch_part = ''.join([py[0] for py in ch_part.split('_')])
    # 拼接非中文字符
    en_part = re.findall(r"[a-zA-Z0-9]+", x)
    en_part = ''.join(en_part)

    
    result = en_part + '_' + ch_part if en_part and ch_part else (ch_part if ch_part else en_part)
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
    print(query_str)
    result = pd.read_sql(query_str, con=con)

    if result.shape[0]>0:

        # 更改中文列名，提供下载用
        result_ch = result.rename(columns=lambda x: c_c_dict[x])
        result_ch.drop('id',axis=1).to_excel('./docs/queried_data.xlsx',
                        index=False, encoding='utf-8')

    
        for col in result.columns[1:]:
            # str类型：英文不变，数字不变，中文转为首字符拼音
            if result[col].dtype == 'O':
                result[f'{col}_sort'] = result[col].apply(format_string)
                max_len = result[f'{col}_sort'].astype(str).apply(lambda x:len(x)).max()
                result[f'{col}_sort'] = result[f'{col}_sort'].astype(str).str.ljust(max_len,'0')
            else:
                max_len = result[col].astype(str).apply(lambda x:len(x)).max()
                result[f'{col}_sort'] = result[col].astype(str).str.zfill(max_len)

    # 保存筛选后的数据
    # 保存json版本，提供排序用
    # result_js = result.drop('id', axis=1)
    # total = result_js.shape[0]
    # rows = result_js.to_dict(orient='records')
    # result_js = {'total': total, 'rows': rows}

    # with open('docs/queried_data.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(result_js))    

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

    # 读取上传的文件
    filename = [file for file in os.listdir('docs/') if 'upload_file' in file][0]
    new_df = pd.read_excel(os.path.join('docs/',filename))
    
    new_df = new_df.rename(columns={'id':'ID'})
    # 给new_df 创建自增id列
    new_df = new_df.reset_index(drop=True).reset_index().rename(columns={'index':'id'})
    data_amount = new_df.shape[0]

    # 提取列名和类型
    col_names = new_df.columns.tolist()
    c_c_dict = {}
    for col in col_names:
        col_en = format_string(col)
        # 防止重名
        col_en = chongming(col_en,c_c_dict)
        c_c_dict[col_en] = col

    reverse_c_c_dict = {value: key for key, value in c_c_dict.items()}
    # 重命名df
    new_df = new_df.rename(columns=lambda x:reverse_c_c_dict[x])

    def format_dtypes(x):
        if 'int' in x:
            return 'int'
        elif 'float' in x:
            return 'float'
        else:
            return 'str'
    # 检测数据类型
    dtype_dict = dict(new_df.dtypes.astype(str).apply(format_dtypes))
    db_en = format_string(form_dict['db_name'])
    # 防止重名
    db_en = chongming(db_en,database_info)
    # 新建数据表
    create_str = f'CREATE TABLE {db_en} (id INT NOT NULL,'
    for col_name in new_df.columns.tolist()[1:]:
        # 判断数据类型
        col_dtype = dtype_dict[col_name]
        if col_dtype in ['int','float']:
            col_dtype = col_dtype.upper()
        else:
            max_len = new_df[col].apply(lambda x:len(str(x))).max()
            if max_len*2 < 1000:
                col_dtype = f'VARCHAR({max_len*2})'
            else:
                col_dtype = f'TEXT({max_len*2})'
        create_str += f"{col_name} {col_dtype} NULL,"

    create_str += 'PRIMARY KEY (id));'
    print(create_str)
    cursor = con.cursor()
    cursor.execute(create_str)
    # 导入数据
    for i in new_df.index:
        value_str = ''
        for col in new_df.columns:
            value_str += f'{eval(dtype_dict[col])(new_df.loc[i,col])},'
            
        insert_str = f"INSERT INTO {db_en} VALUES ({value_str[:-1]});"
        cursor.execute(insert_str)

    con.commit()

    # 构建并更新到database_info.json中
    

    new_db_dict = {db_en: {
        "in_chinese": form_dict['db_name'],
        "desc": form_dict['db_desc'],
        "c_c_dict": c_c_dict,
        "dtype_dict": dtype_dict
    }}
    
    database_info.update(new_db_dict)
    with open('docs/database_info.json','w',encoding='utf-8') as f:
        f.write(json.dumps(database_info,ensure_ascii=False))

    




    
 



