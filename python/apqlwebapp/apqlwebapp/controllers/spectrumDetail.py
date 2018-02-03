# -*- coding: utf-8 -*-

import flask
from flask import request, render_template
from apqlwebapp.model.database import db
from sdss.internal.database.apo.platedb.ModelClasses import *
from sdss.internal.database.apo.apogeeqldb.ModelClasses import *

spectrumDetail_page = flask.Blueprint('spectrumDetail_page', __name__)


def csvSpectrum(exposure_no, fiber_no, session):
        
    exposure = int(exposure_no)
    fiber = int(fiber_no)
        
    spectrum = session.query(QuickredSpectrum).\
                    join(Quickred, Exposure).\
                    filter(Exposure.exposure_no == exposure).\
                    filter(QuickredSpectrum.fiberid == fiber).one()
        
    flux = spectrum.spectrum

    csvList = []
    wl = 0
    for chip in range(3):
        for ii in range(len(flux)):
            csvList.append([wl, flux[ii][chip]])  
            wl += 1     

    return csvList


@spectrumDetail_page.route('/spectrumDetail.html',methods=["POST","GET"])
def spectrumDetail():   
    session=db.Session()  
    return_dict = dict()
    error_messages = []
        
    default_smooth = 3
    nextSpectrum = None
    prevSpectrum = None
        
    exposure = request.args.get(key='exposure', default=None)
    fiber= request.args.get(key='fiber', default=None)
    # Parse form entries
    try:
        exp_no = int(exposure)
    except ValueError:
        exp_no = None
        error_messages.append('Exposure number must be an integer')
                
    try:
        fiberid = int(fiber)
    except ValueError:
        fiberid = None
        error_messages.append('Fiber Number must be an integer')
        
        
    if exp_no is None or exp_no == '' or fiber is None or fiber == '':
        error_messages.append('Exposure number and Fiber not specified')
        return_dict["spectrum"] = None
    else:
        spectrum = session.query(QuickredSpectrum).join(Quickred, Exposure).\
        						filter(Exposure.exposure_no == exp_no).\
        						filter(QuickredSpectrum.fiberid == fiberid).one()
        pmf = session.query(Plate.plate_id,\
            					  Observation.mjd).\
            					  join(PlatePointing,Observation,Exposure).\
            					  filter(Exposure.exposure_no == exp_no).distinct().one()

        #find data for plots
        wl_flux = csvSpectrum(exp_no, fiber, session)
        return_dict['wl_flux'] = wl_flux

    return_dict["spectrum"] = spectrum
            
            
#             if TGSession.has_key('spectrumList'):
#                 try:
#                     specIndex = TGSession['spectrumList'].index((plateID, mjd, fiberid))
#                     if specIndex == len(TGSession['spectrumList']) - 1:
#                         nextSpectrum = None
#                         prevSpectrum = TGSession['spectrumList'][specIndex-1]
#                     elif specIndex == 0:
#                         prevSpectrum = None
#                         nextSpectrum = TGSession['spectrumList'][specIndex+1]
#                     else:
#                         nextSpectrum = TGSession['spectrumList'][specIndex+1]
#                         prevSpectrum = TGSession['spectrumList'][specIndex-1]
#                 except:
#                     pass
#         
#         return_dict["nextSpectrum"] = nextSpectrum
#         return_dict["prevSpectrum"] = prevSpectrum
        
    return_dict["plateID"] = pmf[0]
    return_dict["mjd"] = pmf[1]
    return_dict["fiber_num"] = fiberid
    return_dict["exposure_num"] = exp_no
    return_dict["error_messages"] = error_messages
        
    return render_template('spectrumDetail.html',**return_dict)
