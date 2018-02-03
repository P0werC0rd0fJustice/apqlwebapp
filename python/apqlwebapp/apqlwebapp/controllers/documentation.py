# -*- coding: utf-8 -*-
import flask
from flask import request, render_template

documentation_page = flask.Blueprint('documentation_page', __name__)

@documentation_page.route('/documentation.html',methods=["POST","GET"])
def documentation():
    return_dict = dict() 
       
    error_messages = []
 
    return_dict['error_messages'] = error_messages
    return render_template('documentation.html',**return_dict)
