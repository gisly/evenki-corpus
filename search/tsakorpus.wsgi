python_home = '/home/distribs/my_corpus/tsakonian_corpus_platform/search/venv'

activator = python_home + '/bin/activate_this.py'
with open(activator) as f:
    exec(f.read(), {'__file__': activator})


import sys
# sys.path.insert(0, '.../')
# sys.path.insert(0, '.../app/')
import os
os.chdir('/home/distribs/my_corpus/tsakonian_corpus_platform/search')
sys.path.append('/home/distribs/my_corpus/tsakonian_corpus_platform/search')

from web_app import app as application, get_locale as app_get_locale
from flask_babel import Babel

babel = Babel(application)


@babel.localeselector
def get_locale():
    return app_get_locale()


if __name__ == "__main__":
    application.run(port=7342, host='0.0.0.0', debug=False)