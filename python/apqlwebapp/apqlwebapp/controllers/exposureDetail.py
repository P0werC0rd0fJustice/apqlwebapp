# -*- coding: utf-8 -*-
import math
import itertools

import flask
from flask import request, render_template
from apqlwebapp.model.database import db
from sdss.internal.database.apo.platedb.ModelClasses import *
from sdss.internal.database.apo.apogeeqldb.ModelClasses import *

exposureDetail_page = flask.Blueprint('exposureDetail_page', __name__)


# Creates CSV file for Read Num vs S/N^2 in Quicklook Table
def exposure2ReadSN(exposure_num, session):
    exposure = int(exposure_num)        
    qlooks = session.query(Quicklook.readnum,\
                            Quicklook.snr_standard).\
                            join(Exposure).\
                            filter(Exposure.exposure_no == exposure).distinct().all()
                                     
    csvList = []
    for qlook in sorted(qlooks):
        csvList.append([int(qlook[0]), math.pow(qlook[1],2)])       
 
    return csvList     

# Creates CSV file for H-Mag vs. S/N^2 in Quickred Table
def exposure2HmagSN(exposure_num, session):
    exposure = int(exposure_num)    
    qreads = session.query(QuickredSpectrum.fiberid,\
                            QuickredSpectrum.medsnr).\
                            join(Quickred,Exposure).\
                            filter(Exposure.exposure_no == exposure).\
                            distinct().all()
    plateholes = session.query(Fiber.fiber_id,\
                            PlateHole.tmass_h).\
                            join(PlateHole,PlPlugMapM,Plugging,Observation,Exposure).\
                            filter(Exposure.exposure_no == exposure).distinct().all()
                                     
    # Organize into a list of lists i.e. [tmass_h, sn^2] for each fiber
    #------------------------------------------------------------------
    # Turn into a list of list of strings
    qreads = [[str(s) for s in x] for x in sorted(qreads)]
    plateholes = [[str(s) for s in x] for x in sorted(plateholes)]
        
    result={}
    for item in itertools.chain(qreads,plateholes):
        result.setdefault(item[0],item[:1]).extend(item[1:])
            
    result = [x for x in result.values() if len(x) > 2]
    result=sorted(result, key=lambda x:float(x[2]))

    csvList = []
        
    for fib in result:
        try:
            if float(fib[2]) > -20 and float(fib[1]) > 0:
                csvList.append([float(fib[2]), math.log(float(fib[1]),10)])
            else:
                pass
        except:
            pass
  
    return csvList
  


@exposureDetail_page.route('/exposureDetail.html',methods=["POST","GET"])
def exposureDetail():   
    session=db.Session()     
    return_dict = dict()
    error_messages = []
    exposure_num = request.args.get(key='exposure_num', default=None)        
        
    #print error_messages
    return_dict['exposure_num'] = exposure_num
    return_dict["error_messages"] = error_messages

    #find data for plots
    if exposure_num is not None and exposure_num != '':
        read_sn = exposure2ReadSN(exposure_num, session)
        return_dict['read_sn'] = read_sn
        hmag_sn = exposure2HmagSN(exposure_num, session)
        return_dict['hmag_sn'] = hmag_sn

    return render_template('exposureDetail.html',**return_dict)