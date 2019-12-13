**Установка на Mac OSX**


Запустить 

_git clone git@face-recognition-demo_

_cd face-recognition-demo_

_python3 -m pip install virtualenv_

_python3 -m virtualenv .env_

_source .env/bin/activate_

_pip install -r requirements.txt_

Для установки dlib сначала скачать с сайта X11 https://www.xquartz.org/

затем скачать dlib http://dlib.net/ распаковать и собрать руками из корня:
_python setup.py install_ 


Если нет eventlet
_pip install eventlet_ 


Запустить монгу 

_docker run --name some-mongo --rm -p 27017:27017 mongo_
