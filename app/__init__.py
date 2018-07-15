# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:09'
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from werkzeug.security import generate_password_hash
import pymysql
# pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/movies"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "38069eb3191a48dc9fc11b4efa68facd"
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config['IMG_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")

db = SQLAlchemy(app)
app.debug = False



from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("home/404.html"), 404


