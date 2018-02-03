#!/usr/bin/env python
""" create  a csv file containing all the targets for all the apogee plates """
import numpy as np
from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
from sdss.internal.database.apo.platedb.ModelClasses import Plate,PlateToSurvey,Survey,PlatePointing,Observation
from apqlwebapp.apqlwebapp.lib.path_generators import plateholes_file_path_gen
from sdss.utilities.yanny import yanny

outfile = '../python/apqlwebapp/apqlwebapp/static/data/targets.csv'


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
f = open(outfile,'wb')
f.write('target,ra,dec,hmag,plate,field\n')
for plate,field in obs_query:
    #plate_holes_files.append(plateholes_file_path_gen(plate))

    file = plateholes_file_path_gen(plate)
    print plate
    plate_holes_yanny = yanny(file)
    plate_holes = plate_holes_yanny.list_of_dicts('STRUCT1')
    for plate_hole in plate_holes:
        if plate_hole['targetids'][0:5] == '2MASS':  
            target =  plate_hole['targetids'].replace('ASS-J','').strip()
            f.write('%s,%.4f,%.4f,%.3f,%s,%s\n' %(target,plate_hole['target_ra'],plate_hole['target_dec'],plate_hole['tmass_h'],plate,field))

f.close()
print '%s written' %outfile