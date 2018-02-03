# -*- coding: utf-8 -*-

"""The application's Globals object"""
import numpy as np
from apqlwebapp.model.database import db
from sdss.internal.database.apo.platedb.ModelClasses import Plate,PlateToSurvey,Survey,PlatePointing,Observation
from apqlwebapp.lib.path_generators import plateholes_file_path_gen
import pickle
import os.path

__all__ = ['Globals']

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    autoscheduler_dir = os.environ['AUTOSCHEDULER_DIR']
    
    front_page_table_header = ["plate_id",\
                            "exposure_num",\
                            "exposure_starttime",\
                            "exposure_time",\
                            "exposure_type",\
                            "qr_snr",\
                            "apr_snr",\
                            "cart"] 

    search_table_header = ["plate_id",\
                        "field",\
    					"exposure_starttime",\
    					"exposure_num",\
    					"medsnr"]
        					
    browse_table_header = ["plate_id",\
                          "field",\
						  "exposure_starttime",\
						  "exposure_num",\
						  "exposure_time",\
						  "exposure_type",\
						  "snr",\
						  "cart"]
                         
    apogee_exposure_flavors = ["Object"]

    apogee_survey_labels = ["APOGEE", "APOGEE-2", "MaNGA", "APOGEE-2S"]

    valid_status_labels = ["Accepted", "Retired", "Bring Back"]

    apogee_lead_modes = ["APOGEE lead"]

    special_plate_types = [{'plate_type':'kep_koi','visit_goal':3500.0,'total_goal':'N/A'},
                           {'plate_type':'manga','visit_goal':'N/A','total_goal':'N/A'}]

    min_good_exptime = 425.0
    exposure_sn_goal = 100.0
    visit_sn2_goal = 3333.333
    double_length_exposure_time = 1000
  
    #Get observered Apogee plates and fields
    session=db.Session()
    plate_holes_files = []
    obs_query = np.array(session.query(Plate.plate_id,Plate.name).\
                                join(PlateToSurvey,Survey,PlatePointing,Observation).\
                                filter(Survey.label.ilike("APOGEE%")).\
                                order_by(Plate.plate_id).distinct().all())

    obs_plates = obs_query[:,0]
    obs_fields = obs_query[:,1]

    #get list of plateholes files for observed Apogee plates only
    for plate,field in obs_query:
        plate_holes_files.append(plateholes_file_path_gen(plate))

    #load up targets dictionary from a pickle file created by bin/createTargetDictionary.py
    apqlwebapp_dir = os.environ['APQLWEBAPP_DIR']
    targets_pickle = os.path.join(apqlwebapp_dir,'python/apqlwebapp/apqlwebapp/static/data/targets.p')
    print 'loading targets.p'
    targets_dict = pickle.load(open(targets_pickle,'rb'))
    print 'loaded'
    last_targets_mod_time = os.path.getmtime(targets_pickle)

    def __init__(self):
    	pass