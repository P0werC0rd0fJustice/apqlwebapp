# -*- coding: utf-8 -*-
"""Controllers for the qlwebapp2 application."""
#!/usr/bin/python
import os

try:
	apqlwebapp_version = os.environ['APQLWEBAPP_DIR'].split("/")[-1]
except:
	apqlwebapp_version = 'not found'	

try:
	spm_version = os.environ['SDSS_PYTHON_MODULE_DIR'].split("/")[-1]
except:
	spm_version = 'not found'	

def addTemplateDictBase(templateDict):
    templateDict["apqlwebapp_version"] = apqlwebapp_version
    templateDict["spm_version"] = spm_version

def getTemplateDictBase():
    templateDict = {}
    addTemplateDictBase(templateDict)
    return templateDict
	