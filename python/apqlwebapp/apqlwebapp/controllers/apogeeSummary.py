#!/usr/bin/python
from __future__ import print_function, division
import flask
from flask import render_template
from ..model.database import db
from sdss.apogee.plate_completion import completion
from sdss.apogee.get_apogee_plates import get_plates
from apqlwebapp.lib.helpers import get_juldate
import astropysics.obstools as obs
import numpy as np
from apqlwebapp.lib.app_globals import Globals
import os

from . import getTemplateDictBase

apogeeSummary_page = flask.Blueprint("apogeeSummary_page", __name__)


# APGPLATE OBJECT DENITION
# DESCRIPTION: APOGEE Plate Object
class apgplate(object):
    # Identifying plate information
    name, locationid, plateid, apgver, platepk = '', 0, 0, 0, -1
    survey_mode, survey = -1, 'apg'
    # Plate pointing information
    ra, dec, ha, maxha, minha = 0.0, 0.0, 0.0, 0.0, 0.0
    # Scheduling info
    vplan, vdone, manual_priority, priority, plugged, sn = 0, 0, 0, 0.0, 0, 0.0
    snql, snred = 0.0, 0.0
    hist, cadence, plate_loc = '', '', ''
    stack = 0
    # Determine plate completion percentage (from algorithm in the SDSS python module)
    def pct(self):
        return completion(self.vplan, self.vdone, self.sn, self.cadence)


@apogeeSummary_page.route('/apogeeSummary.html', methods=['GET'])
def func_name():
    templateDict = {}
    session = db.Session()

    errors = []
    apg = get_plates(errors, plan=True, session=session)
    currjd = get_juldate()
    print(currjd)

    for p in apg:
        obsstr = ''
        obsdays = p.hist.split(',')
        reddays = p.reduction.split(',')
        for d in range(len(obsdays)-1):
            if int(reddays[d]) > 0: obsstr += " %s " % obsdays[d]
            else:
                if currjd - float(obsdays[d]) > 10: obsstr += " <span style='color: red'>%s</span> " % obsdays[d]
                else: obsstr += " <span style='color: grey'>%s</span> " % obsdays[d]
        p.obsstr = obsstr

    # Compute metrics
    nstarted, ncomplete, natapo = 0, 0, 0
    for i in apg:
        if i.pct() >= 1: ncomplete += 1
        elif i.pct() > 0: nstarted += 1
        if i.plate_loc == 'APO' and i.lead_survey == 'apg': natapo += 1

    # Adjust S/N so they can be printed
    for i in apg:
        i.snred = np.sqrt(i.snred)
        i.snql = np.sqrt(i.snql)
        i.pctstr = i.pct() * 100

    templateDict = getTemplateDictBase()
    templateDict['nplates'] = len(apg)
    templateDict['nstarted'] = nstarted
    templateDict['ncomplete'] = ncomplete
    templateDict['natapo'] = natapo
    templateDict['plates'] = apg

    # Compute LST distribution
    lst_apo, lst_store, lst_all = np.zeros([24, 4]), np.zeros([24, 4]), np.zeros([24, 4])
    for i in apg:
        if i.lead_survey == 'man': continue
        lst = int(((i.ra + i.ha) / 15 + 24) % 24)
        pctbin = min([i.pct() // 0.33, 4])
        if i.pct() < 1:
            if i.plate_loc == 'APO': lst_apo[lst,pctbin] += max([i.vplan - i.vdone, 1])
            if i.plate_loc == 'APO' or i.plate_loc == 'Cosmic': lst_store[lst,pctbin] += max([i.vplan - i.vdone, 1])
            if i.manual_priority > 4: lst_all[lst,pctbin] += max([i.vplan - i.vdone, 1])
    templateDict['lst_apo'] = lst_apo
    templateDict['lst_store'] = lst_store
    templateDict['lst_all'] = lst_all
    templateDict['max_lst'] = max([np.sum(lst_all[x,:]) for x in range(24)])

    # Compute "forward" LST distribution based on schedule
    apo = obs.Site(32.789278, -105.820278)
    
    schedule_file = os.path.join(Globals.autoscheduler_dir,'schedules/Sch_base.6yrs.txt.frm.dat')
    try: 
        schedule = np.loadtxt(schedule_file)
        jd = get_juldate()
        jd_idx = [x for x in range(schedule.shape[0]) if schedule[x,0] == int(jd)]
        forward_lst = [[x, 0] for x in range(24)]
        if len(jd_idx) > 0:
            for d in range(jd_idx[0], jd_idx[0]+90):
                night_start, night_end = schedule[d,4], schedule[d,5]
                if night_start == 0: continue
                night_length = int((night_end - night_start) * 24 * 60 / 87 + 0.4)
                midpts = night_start + np.arange(night_length)*(87/60/24) + 0.5/24
                nightlst = [apo.localSiderialTime(x) for x in midpts]
                for l in nightlst: forward_lst[int(l)][1] += 1
    except:
        forward_lst = ''
        errors.append('autoscheduler file not found: '+ schedule_file)

    templateDict['forward_lst'] = forward_lst
    templateDict['errors'] = errors

    return render_template("apogeeSummary.html", **templateDict)