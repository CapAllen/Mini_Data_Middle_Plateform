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
    
    table_name = form_dict['db_name']
    select_str = ''
    where_str = ''

    for col, query in list(form_dict.items())[1:]:
        query = ' ' if not query else query.replace(' ','')
        # select 部分
        if query[0].upper() != 'X':
            select_str = select_str + col + ','
        
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

    
    select_str = select_str[:-1]
    where_str = where_str[:-4]
    
    if where_str:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name} WHERE {where_str}'
    else:
        query_str = f'SELECT {select_str} FROM gaokao.{table_name}'
    result = pd.read_sql(query_str,con=con)

    return result

