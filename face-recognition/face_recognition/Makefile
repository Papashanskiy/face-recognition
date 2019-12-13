CONTAINER_NAME = face-recognition-unit
IAM = $(shell id -u)

build:
	docker build -f Dockerfile -t $(CONTAINER_NAME)  .

bash:
	docker run --rm -i --user $(IAM) -t $(CONTAINER_NAME) bash

run:
	docker run --rm -i --user $(IAM) -t $(CONTAINER_NAME)

migrations:
	cd src/face_recognition && PYTHONPATH=../ DJANGO_SETTINGS_MODULE=settings python ./manage.py makemigrations

shell:
	cd src/face_recognition && PYTHONPATH=../ DJANGO_SETTINGS_MODULE=settings python ./manage.py shell