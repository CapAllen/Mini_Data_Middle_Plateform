# -*- coding: utf-8 -*-
import os
import copy
import zipfile
from database import *
from scrap_funcs import *
from flask import Flask, request, render_template, jsonify, json, redirect, url_for
from flask import send_file, send_from_directory, make_response
from werkzeug import secure_filename
app = Flask(__name__)


def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()

@app.route('/')
def homepage():

    # 读取新闻
    with open('docs/official_news.json', encoding='utf-8') as f:
        official_news = json.load(f)

    # 读取门户新闻
    with open('docs/menhu_news.json', encoding='utf-8') as f:
        menhu_news = json.load(f)

    return render_template('homepage.html',
                           official_news=official_news,
                           menhu_news=menhu_news)


@app.route('/database_manager')
def go_database_manager():

    # connect mysql
    con = pymysql.connect(
        host=config.HOST,
        user=config.USER,
        password=config.PW,
        database=config.DB)

    tables = pd.read_sql('show tables', con=con)['Tables_in_gaokao']

    con.close()
    return render_template(
        'database_manager.html',
        tables=tables,
        database_info=database_info,

    )


@app.route('/crud')
def go_crud():
    if request.method == 'GET':
        table_name = request.args.get('db_name', '')
        table_name_ch = database_info[table_name]['in_chinese']
        cc_lst = list(database_info[table_name]['c_c_dict'].items())[1:]
        return render_template('crud.html',
                               table_name=table_name,
                               table_name_ch=table_name_ch,
                               cc_lst=cc_lst)


@app.route('/crud_result', methods=['GET', 'POST'])
def go_crud_result():
    if request.method == 'POST':
        print(request.form)
        table_name = request.form['db_name']
        table_name_ch = database_info[table_name]['in_chinese']
        cc_lst = list(database_info[table_name]['c_c_dict'].items())[1:]

        result_data = query_data(request.form)

        # 保存最近一次的筛选信息
        imut_str = str(request.form)
        r.set('recent_query', str(dict(eval(imut_str[imut_str.index('('):]))))

        print(result_data.shape)
        print(result_data.columns)
        c_c_dict = database_info[table_name]['c_c_dict']
        c_c_dict_render = c_c_dict

        
        if 'yxdm' in result_data.columns:
            c_c_dict_with_common = copy.deepcopy(c_c_dict)
            c_c_dict_with_common.update(database_info['gdyxjbxx__1']['c_c_dict'])
            c_c_dict_render = c_c_dict_with_common
        
        return render_template('crud_result.html',
                               table_name=table_name,
                               table_name_ch=table_name_ch,
                               cc_lst=cc_lst,
                               c_c_dict=c_c_dict_render,
                               result_data=result_data)
        #    ,
        #    database_info=database_info)


@app.route('/crud_edit', methods=['GET', 'POST'])
@app.route('/crud_delete', methods=['GET', 'POST'])
def go_crud_edit():
    if request.method == 'POST':

        # 读取最近一次的筛选信息
        recent_query = eval(r.get('recent_query'))

        table_name = recent_query['db_name']
        table_name_ch = database_info[table_name]['in_chinese']
        cc_lst = list(database_info[table_name]['c_c_dict'].items())[1:]

        edit_dict = request.form
        print(edit_dict)
        # 检查是否有选中项（删除项）
        imut_str = str(edit_dict)
        imut_tuple = eval(imut_str[imut_str.index('('):])
        delete_ids = [x[1] for x in imut_tuple if x[0] == 'select']

        # 依据edit_dict进行mysql操作
        edit_data(table_name, edit_dict, delete_ids)

        # 按最近一次的筛选条件返回操作后的数据
        result_data = query_data(recent_query)

        c_c_dict = database_info[table_name]['c_c_dict']
        c_c_dict_render = c_c_dict

        
        if 'yxdm' in result_data.columns:
            c_c_dict_with_common = copy.deepcopy(c_c_dict)
            c_c_dict_with_common.update(database_info['gdyxjbxx__1']['c_c_dict'])
            c_c_dict_render = c_c_dict_with_common

        return render_template('crud_edit.html',
                               table_name=table_name,
                               table_name_ch=table_name_ch,
                               cc_lst=cc_lst,
                               c_c_dict=c_c_dict_render,
                               database_info=database_info,
                               result_data=result_data
                               )


@app.route("/direct_download",  methods=['GET', 'POST'])
def direct_download_file():
    result_data = query_data(request.form)

    filename = 'queried_data.xlsx'
    response = make_response(send_from_directory(
        './docs/', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode().decode('latin-1'))
    return response


@app.route("/download/<filename>",  methods=['GET', 'POST'])
def download_file(filename):

    if filename == 'xian_edu_tzgg.zip':
        zip_dir('./docs/xian_edu','./docs/xian_edu_tzgg.zip')
    elif filename == 'zhihu_user.zip':
        zip_dir('./docs/zhihu','./docs/zhihu_user.zip')
    elif filename == 'sneac.zip':
        zip_dir('./docs/sneac_edu','./docs/sneac.zip')
    else:
        pass
    
    response = make_response(send_from_directory(
        './docs/', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode().decode('latin-1'))
    return response


@app.route("/upload")
def go_upload():
    return render_template('upload.html')


@app.route('/crud_batch_upload', methods=['GET', 'POST'])
def go_crud_batch_upload():
    
    # 读取最近一次的筛选信息
    recent_query = eval(r.get('recent_query'))

    table_name = recent_query['db_name']
    table_name_cn = database_info[table_name]['in_chinese']
    columns_lst_cn = '，'.join(list(database_info[table_name]['c_c_dict'].values())[1:])

    return render_template(
        'crud_batch_upload.html',
        table_name=table_name,
        table_name_cn=table_name_cn,
        columns_lst_cn=columns_lst_cn

    )


@app.route("/crud_create",  methods=['POST'])
def go_crud_create():

    # connect mysql
    con = pymysql.connect(
        host=config.HOST,
        user=config.USER,
        password=config.PW,
        database=config.DB)

    upload_file = request.files.get('upload_file')
    filename = 'upload_file' + '.' + \
        upload_file.filename.split('.')[-1]  # 获取文件名
    filelocation = os.path.join('docs/', filename)
    upload_file.save(filelocation)  # 保存文件

    edit_dict = request.form

    if edit_dict.get('tag'):
        # 批量添加
        batch_upload_data(edit_dict)
    else: 
        # 新建数据库
        create_data(edit_dict)

    tables = pd.read_sql('show tables', con=con)['Tables_in_gaokao']
    con.close()

    return render_template(
        'crud_create.html',
        tables=tables,
        database_info=database_info)


@app.route('/xian_edu_spyder')
def go_xian_edu_spyder():

    return render_template(
        'xian_edu_spyder.html',

    )

@app.route('/sneac_spyder')
def go_sneac_spyder():

    return render_template(
        'sneac_spyder.html',

    )

@app.route('/zhihu_activities')
def go_zhihu_activities():

    return render_template(
        'zhihu_activities.html',

    )

@app.route('/zhihu_qas')
def go_zhihu_qas():

    return render_template(
        'zhihu_qas.html',

    )

@app.route('/help', methods=['GET', 'POST'])
def go_help():

    return render_template(
        'help.html',

    )

per_data = {}

@app.route('/progress_data/<uuid>')
def progress_data(uuid):
    
    split_lst = uuid.split('&')
    # 检查标志位
    
    if split_lst[-1] == 'xian_edu':
        uuid,start_date,end_date = split_lst[:-1]
        print(start_date,end_date)
        scraper = xian_edu_scraper(start_date,end_date)
    elif split_lst[-1] == 'zhihu_activities':
        uuid,user_name = split_lst[:-1]
        user_homepage = f'https://www.zhihu.com/people/{user_name}'
        user_info_data = get_user_details(user_homepage)
        start_url = user_info_data.loc[0,'start_url']
        scraper = scrap_user_activities(start_url)
    elif split_lst[-1] == 'zhihu_qas':
        uuid,question_id = split_lst[:-1]
        question_url = f'https://www.zhihu.com/question/{question_id}'
        scraper = get_question_answers(question_url)
    elif split_lst[-1] == 'sneac':
        uuid,start_date,end_date,tpe = split_lst[:-1]
        scraper = sneac_spyder(start_date,end_date,tpe)
    else:
        pass
    for total,done in scraper:
        num_progress = round(int(done) * 100 / int(total), 2)
        print(num_progress)
        per_data[uuid] = num_progress
        print('xxxxxxxxxxxxxxxxxxxxxx')
    return jsonify({'res': num_progress})


@app.route('/show_progress/<uuid>')
def show_progress(uuid):
    print(per_data)
    return jsonify({'res': per_data[uuid]})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
