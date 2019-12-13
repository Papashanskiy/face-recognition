FROM python:3.6-jessie

RUN apt-get update && \
        apt-get install -y \
        libpq-dev \
        uwsgi-plugin-python3  \
        locales

RUN pip install pytz pillow requests gunicorn "django>2.0" django-environ whitenoise psycopg2-binary
RUN pip install raven

EXPOSE 80
ADD src /app
ADD requirements.txt /app

RUN pip install -r /app/requirements.txt

ENV PYTHONPATH /app:$PYTHONPATH
WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=face_recognition.settings

CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:80", "face_recognition.wsgi:application" ]