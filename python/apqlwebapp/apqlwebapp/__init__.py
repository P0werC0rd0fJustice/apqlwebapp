#!/usr/bin/python

from __future__ import print_function
import os
import sys
import socket
from inspect import getmembers, isfunction

import flask

import jinja_filters
from .color_print import print_warning, print_error, print_info

# creates the app instance using the name of the module
#app = Flask(__name__)

# -----------------------------------------
# The snippet below is to hide the warning:
# /usr/local/python/lib/python2.7/site-packages/sqlalchemy/engine/reflection.py:40: SAWarning: Skipped unsupported reflection of expression-based index q3c_spectrum_idx
# WARNING: SAWarning: Skipped unsupported reflection of expression-based index q3c_psc_idx [sqlalchemy.util.langhelpers]
# -----------------------------------------
import warnings
warnings.filterwarnings(action="ignore", message="Skipped unsupported reflection")
warnings.filterwarnings(action="ignore", message='Predicate of partial index')
# -----------------------------------------

def create_app(debug=False, dev=False):
    app = flask.Flask(__name__)

    app.debug = debug

    print("{0}App '{1}' created.{2}".format('\033[92m', __name__, '\033[0m')) # to remove later

    # Define custom filters into the Jinja2 environment.
    # Any filters defined in the jinja_env submodule are made available.
    # See: http://stackoverflow.com/questions/12288454/how-to-import-custom-jinja2-filters-from-another-file-and-using-flask
    custom_filters = {name: function
                      for name, function in getmembers(jinja_filters)
                      if isfunction(function)}
    app.jinja_env.filters.update(custom_filters)

    if app.debug == False:
        # ----------------------------------------------------------
        # Set up getsentry.com logging - only use when in production
        # ----------------------------------------------------------
        from raven.contrib.flask import Sentry

#        dsn = 'https://5f6797382e7d4d92953e746b5c9cae43:588337c20d124c95870453be32b21d50@app.getsentry.com/39984'
        dsn = 'https://6442c6d07a014943b52e9416b574a082:bb93fecf95aa48cf957bf421d9534bea@app.getsentry.com/39993'
        app.config['SENTRY_DSN'] = dsn
        sentry = Sentry(app)
    	print('running Sentry')

        # --------------------------------------
        # Configuration when running under uWSGI
        # --------------------------------------
        try:
            import uwsgi
            app.use_x_sendfile = True
        except ImportError:
            # not running under uWSGI (and presumably, nginx)
            pass

    # Change the implementation of "decimal" to a C-based version (much! faster)
    try:
        import cdecimal
        sys.modules["decimal"] = cdecimal
    except ImportError:
        pass # no available

    # Determine which configuration file should be loaded based on which
    # server we are running on. This value is set in the uWSGI config file
    # for each server.

    if app.debug: #args['debug']:
        hostname = socket.gethostname()
        if "sdss.utah.edu" in hostname:
            server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              'dev-utah.sdss.edu.cfg')
        elif "sdss-db4" in hostname or "sdss4-db" in hostname:
            if dev == False:
                server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              'sdss-db4.local.cfg')
            else:
                server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              'sdss-db4-dev.local.cfg')
        else:
            server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              'localhost.cfg')
    else:
        try:
            import uwsgi
            server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'configuration_files',
                                              uwsgi.opt['flask-config-file']) # to set
        except ImportError:
            print_error("Trying to run in production mode, but not running under uWSGI.\n"
                       "You might try running again with the '--debug' flag.")
            sys.exit(1)

    print("Loading config file: {0}".format(server_config_file))
    app.config.from_pyfile(server_config_file)

    #print(app.config)
    print("Server_name = {0}".format(app.config["SERVER_NAME"]))

    # This "with" is necessary to prevent exceptions of the form:
    #    RuntimeError: working outside of application context
    with app.app_context():
        from .model.database import db

    # -------------------
    # Register blueprints
    # -------------------
    from .controllers.index import index_page
    from .controllers.documentation import documentation_page
    from .controllers.search import search_page
    from .controllers.browse import browse_page
    from .controllers.targets import targets_page
    from .controllers.exposureDetail import exposureDetail_page
    from .controllers.spectrumDetail import spectrumDetail_page 
    from .controllers.apogeeSummary import apogeeSummary_page     

    app.register_blueprint(index_page)
    app.register_blueprint(documentation_page)
    app.register_blueprint(search_page)
    app.register_blueprint(browse_page)
    app.register_blueprint(targets_page)
    app.register_blueprint(exposureDetail_page)
    app.register_blueprint(spectrumDetail_page)
    app.register_blueprint(apogeeSummary_page)

    return app

# Perform early app setup here.
