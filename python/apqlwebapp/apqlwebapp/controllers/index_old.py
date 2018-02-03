#!/usr/bin/python

import flask
from flask import request, render_template

index_page = flask.Blueprint("index_page", __name__)

@index_page.route('/')
def func_name():
    ''' This is the index page, it doesn't do much '''
    templateDict = {}
    return render_template("index.html", **templateDict)