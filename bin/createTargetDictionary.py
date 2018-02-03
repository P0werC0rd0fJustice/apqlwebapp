#!/usr/bin/env python
""" create a dictionary containing target information extracted from plate holes files """
import numpy as np
from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
from sdss.internal.database.apo.platedb.ModelClasses import Plate,PlateToSurvey,Survey,PlatePointing,Observation
from apqlwebapp.lib.path_generators import plateholes_file_path_gen
from sdss.utilities.yanny import yanny
import pickle

outfile = '../python/apqlwebapp/apqlwebapp/static/data/targets.p'

#Get observered Apogee plates and fields
session=db.Session()

obs_query = np.array(session.query(Plate.plate_id,Plate.name).\
                            join(PlateToSurvey,Survey,PlatePointing,Observation).\
                            filter(Survey.label.ilike("APOGEE%")).\
                            order_by(Plate.plate_id).distinct().all())

obs_plates = obs_query[:,0]
obs_fields = obs_query[:,1]

#get list of plateholes files for observed Apogee plates only
targets_dict = dict()

for plate,field in obs_query:
    file = plateholes_file_path_gen(plate)

    if file:
        print plate
        plate_holes_yanny = yanny(file)
        plate_holes = plate_holes_yanny.list_of_dicts('STRUCT1')
        for plate_hole in plate_holes:
            if plate_hole['targetids'][0:5] == '2MASS':  
                target =  plate_hole['targetids'].replace('ASS-J','').strip()
                try:
                    target_plates = targets_dict[target]['plate']
                    target_fields = targets_dict[target]['field']
                except KeyError:
                    target_plates = []
                    target_fields = []
                target_plates.append(plate)
                target_fields.append(field) 
                targets_dict[target] = {'ra':plate_hole['target_ra'],'dec':plate_hole['target_dec'],'plate':target_plates, 
                						'field':target_fields, 'hmag':plate_hole['tmass_h']}
print 'pickling...'
pickle.dump(targets_dict,open(outfile,'wb'))
print 'pickled'
