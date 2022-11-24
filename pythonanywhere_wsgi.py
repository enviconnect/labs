# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Web2py project

import os
import sys

# add your project directory to the sys.path
project_home = '/home/enviConnect/public-EnergyRnDFacilitiesExplorer'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

sys.stdout = sys.stderr
os.chdir(project_home)

# serve web2py via WSGI handler
from app import app
application = app.server
