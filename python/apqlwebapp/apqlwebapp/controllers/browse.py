# -*- coding: utf-8 -*-

from sdss.utilities.convert import datetime2mjd
import math
from collections import defaultdict
from sdss.internal.database.apo.platedb.ModelClasses import Exposure
from apqlwebapp.model.database import db
from apqlwebapp.lib.helpers import baseBrowseQuery, tableRows2tableDict
import flask
from flask import request, render_template
from sqlalchemy import func
import datetime
from . import getTemplateDictBase

browse_page = flask.Blueprint('browse_page', __name__)

def searchMJD(date,session, return_dict):
    error_messages = []
            
    date_numbers = [int(x) for x in date.split("/")]
 
    # Convert the date to MJD (add 1 because observations start at night, by which time we have moved on to next MJD)
    try:
        mjd = (datetime2mjd(datetime.datetime.strptime(date, '%m/%d/%Y')))+1
    except:
        error_messages.append("Date must be formatted like %mm/%dd/%YYYY")
        mjd = ''
            
    if len(error_messages) == 0:
        query_base = baseBrowseQuery(session)
        table_rows = query_base.filter(func.floor(Exposure.start_time/86400.0+0.3)==mjd).all()        
        table_row_list = tableRows2tableDict(table_rows, 'browse')
    else:
        table_row_list = []

    table_row_dict = dict()
    for exp in table_row_list:
        try:
            table_row_dict[exp['plate_id']].append(exp)
        except KeyError:
            table_row_dict[exp['plate_id']] = [exp]
      
    sn_plate_dict = defaultdict(int)
    for plate in table_row_dict.keys():
        try:
            sn_plate_dict[plate] = round(math.sqrt(sum([math.pow(x['snr'],2) for x in table_row_dict[plate]])),3)
        except:
            sn_plate_dict[plate] = '-'
        
    return_dict['sn_total'] = sn_plate_dict
    return_dict['mjd'] = mjd
    return_dict['date_numbers'] = date_numbers
    return_dict['exposure_table_rows'] = table_row_dict 

    return return_dict


@browse_page.route('/browse.html',methods=["POST","GET"])
def browse(): 
    session=db.Session()
 
    return_dict = getTemplateDictBase()
    return_dict['exposure_table_rows'] = []
    return_dict['date_numbers'] = ['','','',]

    date = request.args.get(key='date', default=None)
    
    if date is not None and date != '':
        searchMJD(date,session, return_dict)

    return render_template('browse.html',**return_dict)
  