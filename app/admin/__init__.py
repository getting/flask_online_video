# -*- coding: utf-8 -*-
__author__ = 'limrn'
__date__ = '18-3-25 上午10:12'
from flask import Blueprint



admin = Blueprint('admin', __name__)
import app.admin.views
