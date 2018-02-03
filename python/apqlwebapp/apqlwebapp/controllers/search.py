# -*- coding: utf-8 -*-

import flask
from flask import request, render_template, jsonify
from apqlwebapp.lib.helpers import baseExposureQuery, tableRows2tableDict, apogeePlateIds
from apqlwebapp.lib import app_globals
from apqlwebapp.model.database import db
from . import getTemplateDictBase
from sdss.internal.database.apo.platedb.ModelClasses import *
from sdss.internal.database.apo.apogeeqldb.ModelClasses import QuickredSpectrum, Quickred
from apqlwebapp.lib.path_generators import plateholes_file_path_gen
from sqlalchemy import func
from sdss.utilities.yanny import yanny
import os

search_page = flask.Blueprint('search_page', __name__)

@search_page.route('/plateid2mjds',methods=["POST","GET"])
def plateid2mjds():
    session=db.Session()
    plateid = request.args.get(key='plateid', default=None)
    if plateid is not None and plateid != '':
        mjd_list = sorted([int(x[0]) for x in session.query(func.floor(Exposure.start_time/86400.0+0.3)).\
                                          join(Observation, PlatePointing, Plate, ExposureFlavor).\
                                          filter(Plate.plate_id == int(plateid)).\
                                          filter(ExposureFlavor.label.in_(app_globals.Globals.apogee_exposure_flavors)).\
                                          distinct().all()])
    else:
        mjd_list = []
    return jsonify({'mjd_list' : mjd_list})

@search_page.route('/mjd2plateids',methods=["POST","GET"])
def mjd2plateids():
    session=db.Session()
    mjd = request.args.get(key='mjd', default=None)
    if mjd is not None and mjd != '':
        plate_list = sorted([int(x[0]) for x in session.query(Plate.plate_id).\
                                            join(PlatePointing, Observation, Exposure, ExposureFlavor).\
                                            filter(ExposureFlavor.label.in_(app_globals.Globals.apogee_exposure_flavors)).\
                                            filter(func.floor(Exposure.start_time/86400.0+0.3) == int(mjd)).\
                                            distinct().all()])
    else:
        plate_list = ''
    return jsonify({'plate_list' : plate_list})


@search_page.route('/exposure2quickred',methods=["POST","GET"])
def exposure2quickred():
    session=db.Session()
    exposure_num = request.args.get(key='exposure_num', default=None)  

    quickred_list = session.query(QuickredSpectrum.fiberid,\
                                    QuickredSpectrum.medsnr).\
                                    join(Quickred,Exposure,Observation,PlatePointing,Plate).\
                                    filter(Exposure.exposure_no == int(exposure_num)).\
                                    distinct().all()

    #if no quickred data, just get fibers, and set s/n to '-'
    if len(quickred_list) == 0:
        quickred_list = session.query(Fiber.fiber_id).\
                                    join(PlPlugMapM,Plugging,Observation,Exposure).\
                                    filter(Exposure.exposure_no == int(exposure_num)).\
                                    distinct().all()
        for i,f in enumerate(quickred_list): quickred_list[i] = (f[0],'-')


    #get targets from plateHoles file and match to fiber using xfocal and yfocal
    target_info_dict = dict()
    try:
        plateid = request.args.get(key='plateid', default=None)

        plate_holes_file=plateholes_file_path_gen(plateid)
        plate_holes_yanny = yanny(plate_holes_file)
        plate_holes = plate_holes_yanny.list_of_dicts('STRUCT1')                                
        
        fiber_list = session.query(Fiber.fiber_id, PlateHole.xfocal, PlateHole.yfocal).\
                            join(PlateHole,PlateHolesFile,PlPlugMapM,Plugging,Observation,Exposure).\
                            filter(PlateHolesFile.filename==os.path.basename(plate_holes_file)).\
                            filter(Exposure.exposure_no == int(exposure_num)).distinct().all()
     
        platetype = plate_holes_yanny['platetype']
        if 'APOGEE2' in platetype:
            target2 = 'apogee2_target2'
        else:
            target2 = 'apogee_target2'

        for plate_hole in plate_holes:
            if plate_hole['holetype'] == 'APOGEE' and plate_hole['targettype'] != 'sky':
                #check if star is telluric
                try:
                    byteval=plate_hole[target2]
                except:
                    telluric=0
                idx=9
                telluric=((byteval&(1<<idx))!=0)
                try:
                    fiber = [element[0] for element in fiber_list if (float(element[1]) == plate_hole['xfocal'] and float(element[2]) == plate_hole['yfocal'])]
                    if telluric: 
                        target_info_dict[fiber[0]] = [plate_hole['tmass_h'],plate_hole['targetids'].replace('ASS-J',''),'TELLURIC']
                    else:
                     target_info_dict[fiber[0]] = [plate_hole['tmass_h'],plate_hole['targetids'].replace('ASS-J',''),plate_hole['targettype']]
                except:
                    continue
    except:
        print 'Error finding plate_holes_file'
        

    quickred_list_ext = list()
    for iquickred in quickred_list:
        try:            
            quickred_list_ext.append(iquickred + (float(target_info_dict[iquickred[0]][0]), target_info_dict[iquickred[0]][1], (target_info_dict[iquickred[0]][2]).upper()))
        except KeyError:
            quickred_list_ext.append(iquickred + ('SKY','SKY','SKY'))
    return jsonify({'aaData' : quickred_list_ext})    

def searchExposure(plateid, mjd, return_dict):
    session=db.Session()
    error_messages = []
    warning_messages = []

    try:
        plate = int(plateid)
        #print plateid
    except ValueError:
        error_messages.append('Invalid plate id: %s' % plateid)
                
    try:
        mjd = int(mjd)
        #print mjd
    except ValueError:
        error_messages.append('Invalid MJD: %s' % mjd)

    apogee_plates = apogeePlateIds(session)
    if plate in apogee_plates:
        query_base = baseExposureQuery(session)
    else:
        error_messages.append('Apogee Plate: {0} not found'.format(plateid))
            
    if len(error_messages) == 0:
        table_rows = query_base.filter(Plate.plate_id == plate).\
                            filter(func.floor(Exposure.start_time/86400.0+0.3) == mjd).\
                            order_by(Exposure.exposure_no).\
                            all()   
        table_row_list = tableRows2tableDict(table_rows, 'search')
    else:
        table_row_list = list()
         
    return_dict['plateid'] = plate
    return_dict['mjd'] = mjd
    return_dict['error_messages'] = error_messages
    return_dict['warning_messages'] = warning_messages
    return_dict['exposure_table_rows'] = table_row_list

@search_page.route('/search.html',methods=["POST","GET"])
def search():
    """Handle the front-page."""
    return_dict = getTemplateDictBase()
    return_dict['error_messages'] = ['Nothing yet']
    return_dict['warning_messages'] = []
    return_dict['plateid'] = ''
    return_dict['mjd'] = ''
    return_dict['spectrum_table_rows'] = []
    return_dict['submit'] = False
    return_dict['current_tab'] = 'plate_tab'

    plateid = request.args.get(key='plateid', default=None)
    mjd = request.args.get(key='mjd', default=None)
    if plateid is not None and plateid !='' and mjd is not None and mjd !='':
        searchExposure(plateid, mjd, return_dict)
    
    current_tab = request.args.get(key='tab', default='plate_tab')  
    return_dict['current_tab'] = current_tab


    return render_template('search.html',**return_dict)
