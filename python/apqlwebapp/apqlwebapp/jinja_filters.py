#!/usr/bin/python
	
"""
This file contains all custom Jinja2 filters.
"""

import operator
import json


def sort_multi(L,*operators):
	print L 
	L.sort(key=operator.itemgetter(*operators))
	print L

"""
converts python Nones to jscript nulls
for some reason, returning a json.dumps of a float
caused production version to crash, but not dev version,
so for not Nones, return the input value
"""
def jsonfilter(value):
	if value == None:
	    return json.dumps(value)
	return value
