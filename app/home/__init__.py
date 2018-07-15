# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:11'
from flask import Blueprint

home = Blueprint("home", __name__)
import app.home.views
