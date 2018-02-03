# -*- coding: utf-8 -*-

"""Helpers used in apqlwebapp"""
from apqlwebapp.lib import app_globals
from sdss.internal.database.apo.platedb.ModelClasses import *
from sdss.internal.database.apo.apogeeqldb.ModelClasses import *
import datetime
import sdss.utilities.convert as sdssconv

def baseFrontPageQuery(session):

    return session.query(Plate.plate_id,\
                         Exposure.exposure_no,\
                         Exposure.start_time,\
                         Exposure.exposure_time,\
                         ExposureFlavor.label,\
                         Quickred.snr_standard,\
                         Reduction.snr,\
                         Cartridge.number).\
                         join(PlatePointing,Observation,Plugging,Cartridge,Exposure,ExposureFlavor).\
                         outerjoin(Quickred, Reduction).\
                         order_by(Exposure.exposure_no).\
                         distinct()

def baseExposureQuery(session):
    
    # Returns a base query SQL query statement
   return session.query(Plate.plate_id,\
                          Plate.name,\
                          Exposure.start_time,\
                          Exposure.exposure_no,\
                          Quickred.snr_standard).\
                          join(PlateToSurvey,Survey,PlatePointing,Observation,Exposure,ExposureFlavor).\
                          outerjoin(Quickred).\
                          filter(Survey.label.ilike("apogee%")).\
                          filter(ExposureFlavor.label.ilike("object")).distinct()
                             
def baseBrowseQuery(session):
        
    return session.query(Plate.plate_id,\
                         Plate.name,\
                         Exposure.start_time,\
                         Exposure.exposure_no,\
                         Exposure.exposure_time,\
                         ExposureFlavor.label,\
                         Quickred.snr_standard,\
                         Cartridge.number).\
                         join(PlatePointing,Observation,Plugging,Cartridge,Exposure,ExposureFlavor).\
                         outerjoin(Quickred).\
                         filter(ExposureFlavor.label.in_(app_globals.Globals.apogee_exposure_flavors)).distinct()


def baseDesignValueQuery(session):

    return session.query(DesignValue.value).\
                        join(DesignField, Design, Plate).distinct()

def getDither(session,exp_no,prev_dither):
    #function to determine dither position

    try:
        dither_shift = session.query(Quicklook.dither_prevexp_header).join(Exposure).\
                            filter(Exposure.exposure_no == exp_no).first()[0]
    except:
        dither_shift = '-'
   
    if dither_shift == 99:
        dither = '-'
    elif dither_shift == 0.5:
        dither = 'B'
        prev_dither = 'A'
    elif dither_shift == -0.5:
        dither = 'A'
        prev_dither = 'B'
    elif dither_shift == 0:
        dither = prev_dither
    else: 
        dither = '-'
        prev_dither = '-'

    return dither, prev_dither

def tableRows2tableDict(table_rows, page_name):
    
        table_row_list = list()
        if page_name.lower() == 'search':
            table_header = app_globals.Globals.search_table_header
        elif page_name.lower() == 'browse':
            table_header = app_globals.Globals.browse_table_header
        elif page_name.lower() == 'frontpage':
            table_header = app_globals.Globals.front_page_table_header
           
        for row in table_rows: 
            newrow=[]
            for item in row:
                #replace Decimals with floats
                if str(type(item)) == "<type 'cdecimal.Decimal'>":
                    item=float(item)
                newrow.append(item)             
            table_row_list.append(dict(zip(table_header, newrow)))
        
 
        return table_row_list
                        
def apogeePlateIds(session):
    return [x[0] for x in session.query(Plate.plate_id).\
                                        join(PlateToSurvey,Survey).\
                                        filter(Survey.label.ilike("APOGEE%")).\
                                        order_by(Plate.plate_id).distinct().all()]

def get_juldate():
    #return current julian date
    dt = datetime.datetime.utcnow()
    current_jd = sdssconv.datetime2jd(dt)
    return current_jd



