import json
import pymysql
import config
import pandas as pd

# read database info
with open('docs/database_info.json', encoding='utf-8') as f:
    database_info = json.load(f)

# connect mysql
con = pymysql.connect(
    host=config.HOST,
    user=config.USER,
    password=config.PW,
    database=config.DB)

# 筛选数据，并返回
def query_data(form_dict):
    
    table_name = form_dict['db_name']
    c_c_dict = database_info[table_name]['c_c_dict']
    select_lst = list(c_c_dict.keys())
    where_str = ''

    for col, query in list(form_dict.items())[1:]:
        query = ' ' if not query else query.replace(' ','')
        # select 部分
        if query[0].upper() == 'X':
            select_lst.remove(col)
        
        # where 部分
        if query[0] == 'i':
            new_query = [f'"{query_col}"' for query_col in query[2:].replace('，',',').split(',')]
            where_str = where_str + col + ' IN (' + \
                 ','.join(new_query) + ')' + 'AND '
        elif query[0] in ['>','<','=','!','！']:
            new_query = f'''{query[0].replace('！','!').replace('!','!=')} "{query[1:]}"'''
            where_str = where_str + col + new_query + 'AND '
        else:
            if query == ' ':
                pass
            else:
                raise Exception('输入有误。')

    
    select_str = ','.join(select_lst)
    where_str = where_str[:-4]
    
    if where_str:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name} WHERE {where_str}'
    else:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name}'
    result = pd.read_sql(query_str,con=con)

    return result

# 修改/删除数据
def edit_data(table_name,form_data,delete_ids):
    
    c_c_dict = database_info[table_name]['c_c_dict']
    select_lst = list(c_c_dict.keys())
    
    # 删除数据
    if delete_ids:
        for delete_id in delete_ids:
            delete_str = f'DELETE FROM gaokao.{table_name} WHERE (id = {delete_id});' 
            cursor = con.cursor()
            cursor.execute(delete_str)
            con.commit()
        print('删除成功')

    # 新旧数据
    new = [x for x in list(form_data.keys())[1:] if 'new' in x]
    old = [x for x in list(form_data.keys())[1:] if x not in new ]
    new = sorted(list(set([x.split('&')[0] for x in new])))
    old = sorted(list(set([x.split('&')[0] for x in old])))

    # 修改一条旧数据
    def edit_old_data(old_id):
        # 对于old数据
        # 筛选出对应id的数据
        tables = pd.read_sql(f'SELECT * FROM gaokao.{table_name} WHERE id={old_id}',con=con)
        # 将其转换为dict
        old_dict = tables.to_dict(orient='records')[0]
        # 新的数据转为dict，然后更新原dict
        new_dict = {key.split('&')[1]:value for key,value in form_data.items() if old_id in key}
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
    max_id = pd.read_sql(f'SELECT MAX(id) FROM gaokao.{table_name}',con=con)
    # 直接replace到数据库中
    for new_id in new:
        new_dict = {key.split('&')[2]:value for key,value in form_data.items() if new_id in key}
        new_dict['id'] = int(max_id.iloc[0,0]) + 1
        keys = ','.join(list(new_dict.keys()))
        values = ','.join([f"'{val}'" for val in list(new_dict.values())])
        replace_str = f'REPLACE INTO gaokao.{table_name} ({keys}) VALUES ({values})' 
        cursor = con.cursor()
        cursor.execute(replace_str)
        con.commit()
        print('新数据处理完成')


    

