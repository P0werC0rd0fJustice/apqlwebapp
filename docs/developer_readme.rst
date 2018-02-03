===========================================
Apogee QL Webapp - Developer Instructions
===========================================

These notes are meant for the developer maintaining the webapp.  A description of the functionality aimed at the user can be found on the wiki: https://trac.sdss.org/wiki/APOGEE2/apqlwebapp

Development mode
-----------------

To run the webapp in development mode:

  - log in to your sdss4-db.apo.nmsu.edu account

  - if you wish to keep the webapp running after you logoff, you need to open a screen:
     > screen -S apqlwebapp_debug

  - if the apqlwebapp module is not already installed, do so now with:
     > sdss4install -d operations/general/apqlwebapp trunk

  - the webapp required sdss_python_module to be installed too:
     > sdss4install -d sdss/sdss_python_module {tag}

  - load up the apqlwebapp module to set up the environment settings:
     > module load apqlwebapp/trunk

  - start the webapp in debig mode on port 9001 with:
     > $APQLWEBAPP_DIR/python/apqlwebapp/run_apqlwebapp.py -d -p 9001

  - on your own computer, make sure you have an ssh connection to sdss4-db set up in your .ssh/config file.  It should look something like this:
  	Host sdss4-db
     	HostName sdss4-db.apo.nmsu.edu
     	user nshane
     	Port 22
     	ProxyCommand ssh -A nshane@sdss-gateway.apo.nmsu.edu nc %h %p
     	ForwardX11 yes

  - on your own computer, set up a tunnel to port 9001 of sdss4-db (I recommend creating an alias for this in your ~/.bashrc file):
      > ssh -L 9001:localhost:9001 sdss4-db -fN
    

  - the development version of the webapp can then be viewed on a browser on your own computer at http://localhost:9001

  - if you wish to keep your screen running in the background after you log off, hit Crtl-A-D

Production mode
----------------

To run the webapp in production mode:

  - log in to sdss4-db.apo.nmsu.edu as the sdss4 user.

  - if the apqlwebapp module is not already installed, do so now with:
     > sdss4install -d operations/general/apqlwebapp {tag}
	where {tag} is the latest tag number.

  - the webapp required sdss_python_module to be installed too:
     > sdss4install -d sdss/sdss_python_module {tag}

  - load up the apqlwebapp module to set up the environment settings:
     > module load apqlwebapp

  - if you have just installed a new tag, go to $APQLWEBAPP_DIR, and then back up one directory.  Delete the 'current' link directory and create a new one pointing at your new tag
     > ln -s {tag} current

  - the following startup scripts are available for apqlwebapp:
  	/home/sdss4/bin/startup/apqlwebapp-start
  	/home/sdss4/bin/startup/apqlwebapp-stop
  	/home/sdss4/bin/startup/apqlwebapp-restart
  	/home/sdss4/bin/startup/apqlwebapp-status
  	Run apqlwebapp-start to start the webapp if it isn't already running, or apqlwebapp-restart if it is, and you are updating to a new version.

  - the url for the webapp is https://apogeeql.apo.nmsu.edu

  - the pid and logs are written to /var/www/apogee-quicklook/current

  - Details can also be found on the wiki at https://trac.sdss.org/wiki/APO/ServersAndServices#ApogeeQuicklookWebapp


Creating a target dictionary
-----------------------------  
In order for the webapp to be able to link targets to plates quickly, the webapp preloads a dictionary created with information extracted from the plate holes file.  This dictionary is created by the createTargetDictionary.py script that can be found in the /bin directory.  You will occasionally need to re-run this to make sure the dictionary is up to date:
  > python $APQLWEBAPP_DIR/bin/createTargetDictionary.py

This will create a python pickle file, targets.p, in the static/data directory.  The webapp should automatically detect when the file has been updated.  As the file is big, it will take a few (~8) seconds to load.



