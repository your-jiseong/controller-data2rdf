DIR="${PWD}"
# install - bottle
pip install bottle
# install - cherrypy (compatible version with bottle)
cd "${DIR}/CherryPy-3.6.0"
python setup.py install
cd ..
# install - langdetect
pip install langdetect