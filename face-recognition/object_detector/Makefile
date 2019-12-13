CONTAINER_NAME = object-detector-unit
IAM = $(shell id -u)

build:
	docker build -f Dockerfile -t $(CONTAINER_NAME)  .

bash:
	docker run --rm -i -t $(CONTAINER_NAME) bash

run:
	docker run --rm -i  --port 8001:80 --env URL=https://vision-api.invitronet.ru/recognition/recognize/image -t $(CONTAINER_NAME)