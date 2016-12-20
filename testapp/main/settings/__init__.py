# Settings loader file.

import os, sys, glob, re, socket

SPATH = os.path.dirname(__file__)
BASE_DIR = os.path.join(SPATH,'../..')

sys.path.append(os.path.join(BASE_DIR,'..'))
sys.path.append(os.path.join(BASE_DIR,'.dev/'))
print sys.path

# Open and compile each file
machine_name = re.sub('[^A-z0-9._]', '_', socket.gethostname())
for s_file in ['00-base','10-apps','20-drop','local',machine_name]:
  try:
    f = 'main/settings/%s.py'%s_file
    exec(compile(open(os.path.abspath(f)).read(), f, 'exec'), globals(), locals())
  except IOError:
    print "Setting file missing. We looked here: %s"%f
