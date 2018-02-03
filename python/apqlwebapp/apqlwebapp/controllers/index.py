# -*- coding: utf-8 -*-

import flask
from flask import request, render_template, jsonify
from apqlwebapp.lib.helpers import baseFrontPageQuery, baseDesignValueQuery, getDither, tableRows2tableDict
from apqlwebapp.model.database import db
from sdss.internal.database.apo.platedb.ModelClasses import *
import sdss.apogee.plate_completion as pc
import datetime, sys
import sdss.utilities.convert as sdssconv
from apqlwebapp.lib import app_globals
from sqlalchemy import func
#import csv #for loading al_test.txt
from . import getTemplateDictBase

index_page = flask.Blueprint('index_page', __name__)

#get the apogee visit s/n goal from app_globals
visit_sn2_goal = app_globals.Globals.visit_sn2_goal

def getExposuresForPlate(session,plate,error_messages):
    #get a list of exposures for the given plate and calculate S/N statistics
    plate_info_dict = getPlateInfo(session,plate,error_messages)[0]
    ver_plates = plate_info_dict['ver_plates']
    plate_type = plate_info_dict['plate_type']

    try:
       #check plate is Apogee/Manga
        if isApogeePlate(session,plate):
            query_base = baseFrontPageQuery(session)

            table_rows = query_base.filter(Plate.plate_id.in_(ver_plates)).\
                    filter(Exposure.exposure_time > app_globals.Globals.min_good_exptime).\
                    filter(ExposureFlavor.label.in_(app_globals.Globals.apogee_exposure_flavors)).all()
                    
            table_row_list = tableRows2tableDict(table_rows, 'frontpage')
            #look up the planned number of visits
            vplan = getVplan(session,plate)
        else:
            vplan = 0
            table_row_list = []
    except:
        vplan = 0
        table_row_list = []
        error_messages += "Error1: Plate %s, %s" % (plate, str(sys.exc_info()[1]))

    table_row_dict = dict()
    # add some extra fields for each exposure (mjd and s/n info)
    prev_dither = '-'
    datetime_now = datetime.datetime.utcnow().strftime("%M:%S")  # FOR TESTING
    for i,exp in enumerate(table_row_list):
        exp['time'] = datetime_now  # FOR TESTING
        exp_no = exp['exposure_num']
        exp['exposure_mjd'] = int(float(exp['exposure_starttime'])/86400.0 + 0.3)
        exp['exposure_starttime_str'] = sdssconv.mjd2datetime(float(exp['exposure_starttime'])/86400.0).strftime("%Y.%m.%d %H:%M:%S")
        #determine dither position    
        dither, prev_dither = getDither(session,exp_no,prev_dither) 
        exp['dither'] = dither
        if i > 0 and exp['exposure_mjd'] == table_row_list[i-1]['exposure_mjd']:
            table_row_list[i-1]['dither'] = prev_dither
            prev_dither = dither
        #calculate sn2
        if exp['qr_snr'] is not None:
            qr_snr2 = round(exp['qr_snr'] * exp['qr_snr'],1)
            exp['qr_snr2'] = qr_snr2
        else:
            qr_snr2 = 0
            exp['qr_snr2'] = '-'        

        if exp['apr_snr'] is not None:
            apr_snr2 = round(exp['apr_snr'] * exp['apr_snr'],1)
            exp['apr_snr2'] = apr_snr2
            #use full reduction S/N if present, otherwise quickred
            exp['snr2'] = apr_snr2
        else:
            apr_snr2 = 0
            exp['apr_snr2'] = '-' 
            exp['snr2'] = qr_snr2       

        if exp['apr_snr2'] == '-' and exp['qr_snr2'] == '-' :
            exp['quality'] = 'Processing' 
        elif exp['snr2'] != '-' and float(exp['snr2']) >= app_globals.Globals.exposure_sn_goal:
            exp['quality'] = 'Good'
        else:
            exp['quality'] = 'Bad'

        try:
            table_row_dict[exp['exposure_mjd']].append(exp)
        except KeyError:
            table_row_dict[exp['exposure_mjd']] = [exp]

    mjd_dict = dict()
    total_sn2 = 0.0
    vdone = 0

    #if no exposures taken so far
    if len(table_row_dict) == 0:
        #check if the plate is a special plate type, eg kep_koi, with different S/N goals
        if plate_type in [e['plate_type'] for e in app_globals.Globals.special_plate_types]:
            special_dict = [e for e in app_globals.Globals.special_plate_types if e['plate_type'] == plate_type][0]
            exp_visit_sn2 = special_dict['visit_goal']
            exp_total_sn2 = special_dict['total_goal'] 
        else:
            if vplan > 0: 
                exp_visit_sn2 = round(visit_sn2_goal,1)
            else:
                exp_visit_sn2 = 'Error'
            exp_total_sn2 = 0.0

        mjd_dict[0]={'vdone':0, 'vplan':vplan, 'visit_sn2':0.0, 'exp_visit_sn2':exp_visit_sn2,
                 'total_sn2':0.0, 'exp_total_sn2':exp_total_sn2, 'vstatus':0, 'cart':'n/a', 'plate_id':plate}

    #else, calculate S/N statistics and visit number for each MJD
    else:
        for this_mjd in sorted(table_row_dict.keys()):
            sn2 = 0.0
            row_count = 0
            cart = table_row_dict[this_mjd][0]['cart']
            plate_id = table_row_dict[this_mjd][0]['plate_id']

            """ Discard pairs code commented out for now"""
            """
            #If one exposure in a dither pair is Bad, discard the other half of the pair.
            #Since dithers are paired by closest matching S/N, this means discarding the
            #lowest S/N exposures with the opposite dither to the bad exposures. 
            goodA = [x for x in table_row_dict[this_mjd] if x['quality'] == 'Good' and x['dither'] == 'A']
            goodB = [x for x in table_row_dict[this_mjd] if x['quality'] == 'Good' and x['dither'] == 'B']

            if len(goodA) > len(goodB):
                num_discard = len(goodA) - len(goodB)
                goodA_sorted = sorted(goodA, key=lambda k:k['snr2'])
                for i in range(num_discard):
                    goodA_sorted[i]['quality'] = 'Discarded'
            elif len(goodB) > len(goodA):
                num_discard = len(goodB) - len(goodA)
                goodB_sorted = sorted(goodB, key=lambda k:k['snr2'])
                for i in range(num_discard):
                    goodB_sorted[i]['quality'] = 'Discarded'
          
			"""

            #mark any unpaired dithers
            A_dithers = [x for x in table_row_dict[this_mjd] if x['dither'] == 'A']
            B_dithers = [x for x in table_row_dict[this_mjd] if x['dither'] == 'B']
            if len(A_dithers) > len(B_dithers):
                num_unpaired = len(A_dithers) - len(B_dithers)
                A_sorted = sorted(A_dithers, key=lambda k:k['snr2'])
                for i in range(num_unpaired):
                    if A_sorted[i]['quality'] == 'Good':
                        A_sorted[i]['quality'] = 'Unpaired (Good)'
                    else:
                        A_sorted[i]['quality'] = 'Unpaired (Bad)'
            elif len(B_dithers) > len(A_dithers):
                num_unpaired = len(B_dithers) - len(A_dithers)
                B_sorted = sorted(B_dithers, key=lambda k:k['snr2'])
                for i in range(num_unpaired):
                    if B_sorted[i]['quality'] == 'Good':
                        B_sorted[i]['quality'] = 'Unpaired (Good)'
                    else:
                        B_sorted[i]['quality'] = 'Unpaired (Bad)'

            for row in table_row_dict[this_mjd]:
                if row['quality'] == 'Good' or row['quality'] == 'Unpaired (Good)':
                    #use full reduction S/N if present, otherwise quickred
                    sn2 += float(row['snr2'])    
                    row_count += 1
            if row_count >= 2:
                vdone += 1

            visit_sn2 = sn2
            total_sn2 += visit_sn2

            #check if the plate is a special plate type, eg kep_koi, with different S/N goals
            if plate_type in [e['plate_type'] for e in app_globals.Globals.special_plate_types]:
                special_dict = [e for e in app_globals.Globals.special_plate_types if e['plate_type'] == plate_type][0]
                exp_visit_sn2 = special_dict['visit_goal']
                exp_total_sn2 = special_dict['total_goal'] 
            else:
                exp_visit_sn2 = round(visit_sn2_goal,1)
                if vdone < vplan:
                    exp_total_sn2 = round(visit_sn2_goal * vdone,1)
                else:
                    exp_total_sn2 = round(visit_sn2_goal * vplan,1)
     
            #mark any visits with no S/N as bad
            if visit_sn2 > 0:
                vstatus=1
                vdone_str=str(vdone)
            else:
                vstatus=0
                vdone_str='-'
      
            mjd_dict[this_mjd]={'vdone':vdone, 'vdone_str':vdone_str, 'vplan':vplan, 'visit_sn2':round(visit_sn2,1), 'exp_visit_sn2':exp_visit_sn2,
                     'total_sn2':round(total_sn2,1), 'exp_total_sn2':exp_total_sn2, 'vstatus':vstatus, 'cart':cart, 'plate_id':plate_id}

    return table_row_dict, mjd_dict, error_messages

def getLatestPlateFromMjd(session,mjd):
    #find the most recently observed plate for the given mjd
    try:
        query_base = baseFrontPageQuery(session)
        table_rows = query_base.filter(func.floor(Exposure.start_time/86400.0+0.3) == mjd).all()[-1]
        current_plate = table_rows[0]
    except:
        current_plate = None

    #*********for testing ***************   
    '''     
    with open('latestplate_test.txt') as f:
        try:
            current_plate=int(f.read())
        except:
            current_plate=None
    '''
    
    return current_plate

def getActivePluggings(session):
    #find all the APOGEE plates and cartridges in the current active pluggings table
    ap = session.query(Cartridge.number,Plate.plate_id).join(Plugging,ActivePlugging,Plate,PlateToSurvey,Survey).\
                filter(Survey.label.ilike("apogee%")).order_by(Cartridge.number).all()

    #*********for testing ***************
    """   
    with open('al_test.txt') as f:
        reader=csv.reader(f)
        ap=list(reader)
    for item in ap:
        item[0] = int(item[0])
        item[1] = int(item[1])
    """

    return ap

def getPlateInfo(session,plate,error_messages):
    #returns a dictionary containing various plate information
    if not isApogeePlate(session,plate):   
        if plate:
            plate_info_dict = {'loc_id':'', 'version':'', 'field_id':'', 'ver_plates':[plate], 'plate_type':'', 'priority':''}
            error_messages += "Plate %s is not an accepted APOGEE or MANGA plate" %plate
        else:
            plate_info_dict = {'loc_id':'', 'version':'', 'field_id':'', 'ver_plates':[], 'plate_type':'', 'priority':''}
    
        return plate_info_dict, error_messages
    try:
        #find version number for this plate
        version = pc.getPlateVersion(session,plate)

        #find all the APOGEE plates with the same location_id as the current plate
        loc_id,field_id,priority = session.query(Plate.location_id,Plate.name,PlatePointing.priority).\
                            join(PlatePointing).\
                            filter(Plate.plate_id==plate).one()

        loc_plates = session.query(Plate.plate_id).\
                        join(PlateToSurvey,Survey,PlateToPlateStatus,PlateStatus).\
                        filter(Survey.label.ilike("apogee%")).\
                        filter(PlateStatus.label.in_(app_globals.Globals.valid_status_labels)).\
                        filter(Plate.location_id == loc_id).all()
        
        #only return plates with the same version number as original plate
        ver_plates=[]
        try:
            for pl in loc_plates:
                if pc.getPlateVersion(session,pl) == version:
                    ver_plates.append(pl[0])
        except:
            error_messages += 'Warning: Problem locating all plates with the same field, location ID and version as Plate %s, please ensure database has been updated.' %plate

        #get the plate design type
        plate_type = getPlateDesignType(session,plate)

        plate_info_dict = {'loc_id':loc_id, 'version':version, 'field_id':field_id, 'ver_plates':ver_plates, \
                        'plate_type':plate_type, 'priority':priority}
    except:
        plate_info_dict = {'loc_id':'', 'version':'', 'field_id':'', 'ver_plates':[plate], 'plate_type':'', 'priority':''}
        if plate: error_messages += "Error: Plate %s, %s" % (plate, str(sys.exc_info()[1]))

    return plate_info_dict, error_messages

def getVplan(session,plate):
    #look up the planned number of visits
    try:
        dv_base = baseDesignValueQuery(session)
        vplan = int(dv_base.\
            filter(DesignField.label=='apogee_n_design_visits').\
            filter(Plate.plate_id == plate).first()[0])
        return vplan
    except:
        raise RuntimeError("ERROR: unable to find apogee_n_design_visits for plate %s" %plate)

def getPlateDesignType(session,plate):
    #get the plate design type
    dv_base = baseDesignValueQuery(session)
    try:
        design_type = dv_base.\
                        filter(DesignField.label=='apogee_design_type').\
                        filter(Plate.plate_id == plate).distinct().one()[0]
    except:
        design_type = ''
    return design_type   

def isApogeePlate(session,plate):
    #check in the plate is part of the Apogee (or manga) survey
    #also check the plate status is included in the Globals list of valid status values
    apogee_survey = session.query(Plate).join(PlateToSurvey,Survey,PlateToPlateStatus,PlateStatus).\
                    filter(Plate.plate_id == plate).\
                    filter(Survey.label.in_(app_globals.Globals.apogee_survey_labels)).\
                    filter(PlateStatus.label.in_(app_globals.Globals.valid_status_labels)).\
                    count()
    if apogee_survey > 0: return True
    return False

def isDoubleLengthExposure(session,plate):
    #check the apogee_exposure_time design field.  If it is 1000s, then 
    #the plate requires double length exposures
    dv_base = baseDesignValueQuery(session)
    try:
        exposure_time = float(dv_base.\
                            filter(DesignField.label.ilike('apogee_exposure_time')).\
                            filter(Plate.plate_id == plate).distinct().one().value)
        if exposure_time == app_globals.Globals.double_length_exposure_time:
            return 'T'
    except:
        return 'F'
    return 'F'

#create a json webpage of the current active pluggings
@index_page.route('/activelist')
def activeList():
    session=db.Session()

    #get the current active pluggings
    active_list = getActivePluggings(session) 

    plate_dict_list = []
  
    for al in active_list:
        al_plate = al[1]
        al_cart = al[0]

        #add some plate info
        plate_info_dict = getPlateInfo(session,al_plate,'')[0]
        al_platetype = plate_info_dict['plate_type']
        al_priority = plate_info_dict['priority']  
        al_name = plate_info_dict['field_id']


        #is this a double-length-exposure plate?
        al_dab = isDoubleLengthExposure(session,al_plate)


        #add some visits and S/N info
        mjd_info = getExposuresForPlate(session,al_plate,'')[1]
        latest_mjd= max(mjd_info.keys())
        latest_mjd_info = mjd_info[latest_mjd]
        al_sn2 = latest_mjd_info['total_sn2']
        al_vdone = latest_mjd_info['vdone']
        al_vplan = latest_mjd_info['vplan']
        al_completion = round(pc.completion(al_vplan, al_vdone, al_sn2,0) * 100.0, 1)
        al_sn_completion = round(pc.calculateSnCompletion(al_vplan, al_sn2) * 100.0, 1)

        #check if the plate is a special plate type, eg kep_koi, with different S/N goals
        if al_platetype in [e['plate_type'] for e in app_globals.Globals.special_plate_types]:
            special_dict = [e for e in app_globals.Globals.special_plate_types if e['plate_type'] == al_platetype][0]
            al_exp_sn2 = special_dict['total_goal'] 
        else:
            al_exp_sn2 = round((visit_sn2_goal * al_vplan),1)

        plate_dict_list.append({'plate':al_plate, 'cart':al_cart, 'plate_type':al_platetype, 'priority':al_priority, 'name':al_name, 'dab':al_dab, 
                             'vplan':al_vplan, 'vdone':al_vdone, 'current_sn2':round(al_sn2,1), 'exp_sn2': al_exp_sn2, 
                             'pc_completion':al_completion, 'sn_completion':al_sn_completion})

    #find the plate most recently observed today
    datetime_now = datetime.datetime.utcnow()   
    current_mjd =  int(sdssconv.mjd2sdssjd(sdssconv.datetime2mjd(datetime_now))) 
    latest_plate = getLatestPlateFromMjd(session,current_mjd)
    # not interested in latest plate if it is not Apogee/manga
    if not isApogeePlate(session,latest_plate): latest_plate = None
    return jsonify({'platelist':plate_dict_list,'latest_plate':latest_plate})


#create a json webpage of the exposure and mjd info for a selected plate
@index_page.route('/plate_exposures',methods=["POST","GET"])
def plateExposures():
    session=db.Session()
    plate = request.args.get(key='plateid', default=None)

    if plate is not None and plate != '':
        exposures, mjd_info, error_messages = getExposuresForPlate(session,plate,'')

    return jsonify({'exposures':exposures,'mjd_info':mjd_info})


#Handle the front page
@index_page.route('/',methods=["POST","GET"])
def indexPage():
    session=db.Session()
    error_messages = ''
    return_dict = getTemplateDictBase()
    return_dict['ver_plates'] = []
 
    #get current time and SDSS MJD
    datetime_now = datetime.datetime.utcnow()   
    current_mjd =  int(sdssconv.mjd2sdssjd(sdssconv.datetime2mjd(datetime_now))) 
    return_dict['current_mjd'] = current_mjd   

    #if a plate is selected, find exposures for that plate
    #else find for most recent plate used today
    plate = request.args.get(key='plateid', default=None)
    if plate is not None and plate != '':
        try:
            plate = int(plate)
            plate_selected = 1
        except:
            plate = None
            plate_selected = 0
    else:
        plate = getLatestPlateFromMjd(session,current_mjd)
        plate_selected = 0

    return_dict['plate_id'] = plate
    return_dict['plate_selected'] = plate_selected

    #Find all the APOGEE plates with the same location_id and version as the current plate
    #Also find the plate type and priority
    plate_info_dict, error_messages = getPlateInfo(session,plate,error_messages)
    return_dict.update(plate_info_dict)
    return_dict['error_messages'] = error_messages

    return render_template('index.html',**return_dict)