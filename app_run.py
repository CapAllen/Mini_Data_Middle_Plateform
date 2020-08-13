# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify, json, redirect, url_for
# from create_app import app
# from models import db, Event
# from config import PAGE_SIZE, CURRENT_DATE, TABLE_NAME
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

# from flask import Flask

app = Flask(__name__)
# app.config.from_object('config')

@app.route('/')
@app.route('/scan/all/', methods=['GET', 'POST'])
def scan_all():
    if request.method == 'GET':
        
        return render_template('homepage.html')

@app.route('/database_manager')
def go_database_manager():
   
    return render_template(
        'database_manager.html',
       
    )

@app.route('/help')
def go_help():
   
    return render_template(
        'help.html',
       
    )

if __name__ == '__main__':
  app.run(host='127.0.0.1', port = 8080, debug=True)