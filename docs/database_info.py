'''
This file contains basic information of databases in MySQL. 
Such as name, description, columns-Chinese dict.
'''

database_info = {
    'localscore':{
        'in_chinese':'各省录取最低分',
        'desc':'包含2014-2017年间，各大学在各省份分科类录取批次、录取数、最低分及最低位次。'
        'c_c_dict':{
            'id':'id',
            'name':'院校名称',
            'category':'科类',
            'batch':'批次',
            'province_score':'批次线',
            'bkcc':'院校级别',
            'low_score':'最低分',
            'low_wc':'最低位次',
            'luqu_num':'录取数',
            'year':'年份',
            'location':'省份'
        }
    }
}