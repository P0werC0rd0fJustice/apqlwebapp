# -*- coding: utf-8 -*-

import flask
from flask import request, render_template
from apqlwebapp.lib import app_globals
from operator import itemgetter
import pickle
import os
from . import getTemplateDictBase

ag = app_globals.Globals
targets_page = flask.Blueprint('targets_page', __name__)

def searchPlates(plateid, targets_dict, return_dict):     
    return_dict['table_type'] = 'plate'
    table_rows = []
    error_messages = []
    field = ''	
   
    try:
    	int(plateid)
    except:
    	error_messages.append('Plate ID must be an integer')
    	
    apogee_plates = ag.obs_plates

    if plateid in apogee_plates: 

        table_rows=[]

        for target in targets_dict.keys():
            if plateid in targets_dict[target]['plate']:
                table_rows.append((target, targets_dict[target]['ra'], targets_dict[target]['dec'], targets_dict[target]['hmag']))
                field = targets_dict[target]['field'][0]

        if len(table_rows) == 0: error_messages.append('No targets found for plate %s' %plateid)
        

    else:
        error_messages.append('Specified plate is not an observed apogee plate')
	

    return_dict['target_table_rows'] = sorted(table_rows, key=itemgetter(1))
    return_dict['error_messages'] = error_messages
    return_dict['plateid'] = plateid   
    return_dict['field'] = field     
        

def searchTargets(targets, targets_dict, return_dict):
    return_dict['table_type'] = 'target'
    	
    error_messages = []
    warning_messages = []
    table_rows = []

    targets = str(targets).lstrip().rstrip()
        
    if "\n" in targets:
        newline_split = "\n"
    elif "\r" in targets:
        newline_split = "\r"
    else:
        newline_split = "\n"
        
    for line in targets.split(newline_split):
        targ_name = line.strip()
        if targ_name[0:2] != '2M':
            warning_messages.append("%s not a valid target name (must start with 2M)" %targ_name)
            continue 
            
        target_row = []        

        try:
            my_targ = targets_dict[targ_name]
            for plate,field in zip(my_targ['plate'],my_targ['field']):
                row = [(targ_name,my_targ['ra'],my_targ['dec'],my_targ['hmag'],plate,field)]
                if len(row) > 0: target_row.append(row[0])

            target_row.sort(key = itemgetter(3))
                   
            for itarget_row in target_row:
                table_rows.append(itarget_row) 
        except:
            warning_messages.append("Target %s not found" %targ_name)    

    return_dict['target_table_rows'] = table_rows
    return_dict['error_messages'] = error_messages
    return_dict['warning_messages'] = warning_messages
    return_dict['plateid'] = ''

@targets_page.route('/targets.html',methods=["POST","GET"])
def targets():

    return_dict = getTemplateDictBase()
    return_dict['table_type'] = None 
       
    error_messages = []
    table_rows = []
        
    return_dict['target_table_rows'] = table_rows
    return_dict['plateid'] = ''
    return_dict['error_messages'] = error_messages

    if os.path.getmtime(ag.targets_pickle) > ag.last_targets_mod_time:
        print 'NEW PICKLE FILE: loading targets.p'
        ag.targets_dict = pickle.load(open(ag.targets_pickle,'rb'))
        print 'loaded'
        ag.last_targets_mod_time = os.path.getmtime(ag.targets_pickle)

    targets_dict = ag.targets_dict


    plateid = request.args.get(key='plateid', default=None)
    targets = request.args.get(key='targets', default=None)
    if plateid is not None and plateid != '':
        searchPlates(plateid, targets_dict, return_dict)
        return_dict['current_tab'] = 'plate_tab'
    elif targets is not None and targets !='':
        searchTargets(targets, targets_dict, return_dict)
        return_dict['current_tab'] = 'target_tab'
    else:
        return_dict['current_tab'] = 'plate_tab'

    return render_template('targets.html',**return_dict)
