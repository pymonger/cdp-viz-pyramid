import os, sys
from pyramid.paster import get_app

thisDir = os.path.dirname(os.path.abspath(__file__))
application = get_app(
  os.path.join(thisDir, 'production.ini'), 'main')
