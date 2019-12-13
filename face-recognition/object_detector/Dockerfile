FROM python:3.6-jessie

RUN apt-get update && \
        apt-get install -y \
        libpq-dev \
        cmake \
        locales \
        uwsgi-plugin-python3

RUN pip install flask dlib pillow numpy opencv-python
RUN pip install raven

EXPOSE 80
ADD src /app
ADD requirements.txt /app/

RUN pip install -r /app/requirements.txt

ENV PYTHONPATH /app:$PYTHONPATH:/usr/local/lib/python3.6/site-packages
WORKDIR /app

# uwsgi --http-socket 0.0.0.0:8000 --plugins python3 --chdir  /app/object_detector --wsgi app:app --enable-threads

#CMD [ "uwsgi", "--http-socket", "0.0.0.0:8000", \
#               "--chdir", "/app/object_detector", \
#               "--plugins", "python3", \
#               "--max-requests", "10000", \
#               "--buffer-size", "10240", \
#               "--processes", "6", \
#               "--wsgi", "app:app", \
#               "--enable-threads"]

CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:80", "object_detector.app:app" ]

