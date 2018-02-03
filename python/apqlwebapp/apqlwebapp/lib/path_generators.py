# -*- coding: utf-8 -*-
import os

# ===========================================================
# Define a quick function to return a string path to the individual
# plateHoles.par files
# ============================================================
def plateholes_file_path_gen(PlateIdNumber):

        id="{0:06d}".format(int(PlateIdNumber))
        plateFolder =id[0:-2]+'XX'
        filePathName =  os.environ["PLATELIST_DIR"] + "/plates/"+plateFolder+ \
                        "/"+str(id)+"/plateHoles-" + \
                        str(id)+".par"

        return(filePathName)