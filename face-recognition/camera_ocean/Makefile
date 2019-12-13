CONTAINER_NAME = camera-ocean-unit
IAM = $(shell id -u)

build:
	docker build -f Dockerfile -t $(CONTAINER_NAME)  .

bash:
	docker run --rm -i -t $(CONTAINER_NAME) bash

run:
	docker run --rm --env URL=https://vision-api.invitronet.ru/detection/process/image --env VIDEO_SOURCE=rtsp://reader:029113MeV2y@172.17.4.11:554/ -i -t $(CONTAINER_NAME) run --camera-id=1 --forever=1