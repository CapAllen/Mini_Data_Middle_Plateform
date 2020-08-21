# -*- coding: utf-8 -*-
import os
from database import *
from flask import Flask, request, render_template, jsonify, json, redirect, url_for
from flask import send_file, send_from_directory, make_response
from werkzeug import secure_filename
app = Flask(__name__)


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
        table_name = request.form['db_name']
        table_name_ch = database_info[table_name]['in_chinese']
        cc_lst = list(database_info[table_name]['c_c_dict'].items())[1:]

        result_data = query_data(request.form)

        # 保存最近一次的筛选信息
        imut_str = str(request.form)
        r.set('recent_query', str(dict(eval(imut_str[imut_str.index('('):]))))

        print(result_data.shape)

        return render_template('crud_result.html',
                               table_name=table_name,
                               table_name_ch=table_name_ch,
                               cc_lst=cc_lst,
                               database_info=database_info,
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

        print(delete_ids)
        # 依据edit_dict进行mysql操作
        edit_data(table_name, edit_dict, delete_ids)

        # 按最近一次的筛选条件返回操作后的数据
        result_data = query_data(recent_query)

        return render_template('crud_edit.html',
                               table_name=table_name,
                               table_name_ch=table_name_ch,
                               cc_lst=cc_lst,
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


@app.route("/download",  methods=['GET', 'POST'])
def download_file():

    filename = 'queried_data.xlsx'
    response = make_response(send_from_directory(
        './docs/', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        filename.encode().decode('latin-1'))
    return response


@app.route("/upload")
def go_upload():
    return render_template('upload.html')


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
    print('save.')

    edit_dict = request.form
    create_data(edit_dict)

    tables = pd.read_sql('show tables', con=con)['Tables_in_gaokao']

    con.close()

    return render_template(
        'crud_create.html',
        tables=tables,
        database_info=database_info)


@app.route('/help', methods=['GET', 'POST'])
def go_help():

    return render_template(
        'help.html',

    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
