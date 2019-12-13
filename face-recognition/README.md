# Face recognition

## Модули

 * CameraRegistry - хранит списки камер и их соответствие рабочему месту АРМ
 * CameraOcean - читает видеопоток от камер и передаёт картинку в Object Detection Layer
 * Object Detection Layer - вырезает объекты из картинки, передаёт лица в Face Recognition Layer
 * Face Recognition Layer - собственно распознаёт лица, используя внешние API и свои локальные кэши; передаёт информацию о присутствии лица в Face Presence Layer
 * Face Presence Layer - хранит информацию о присутствии "лица" в указанное время в указанной локации; отдаёт виджет в АРМ; получает от АРМ информацию о соответствии фотки и пациента

## Установка 

На убунте:

    $ apt-get install libsm6 libxrender1 cmake


## Local API

### Получить лица за период времени

	GET /faces?from=-10m&to=now

Ответ

	{"faces" : [ {"photo_id": "GUID", "subject_id": "GUID", "images": ["/X.jpg", "/Y.jpg", ...], "created_at": "2017-12-01T03:00", "updated_at": ""}, ] }


### Назначить face_id лицу из базы

	POST /face/mark?photo_id=GUID1&subject_id=GUID2&employer_id=ID

Сохранить факт, что по мнению сотрудника employer_id фотка photo_id содержит изображение субъекта subject_id.


# Запуск

## Запуск camera ocean

    PYTHONPATH=./src/ python src/camera_ocean/cli.py run --input=0 --camera-id=1 --url=http://127.0.0.1:5555/process/image

или

    VIDEO_SOURCE=0 URL='http://127.0.0.1:5555/process/image' CAMERA_ID=1 PYTHONPATH=./src/ python src/camera_ocean/cli.py run

или

    docker run --rm -i -t camera-ocean-unit python camera_ocean/cli.py run --input=rtsp://reader:***@172.17.4.11:554/ --camera-id=1 --url=http://127.0.0.1:5555/process/image

## Запуск object detection unit

    cd src/object_detector && FLASK_APP=app.py FLASK_ENV=development python -m flask run --port 5555

    docker run --rm -i --env FLASK_APP=app.py --env FLASK_ENV=development -t object-detector-unit  python -m flask run --port 8000


## Запуск face recognition unit

    cd src/face_recognition && DJANGO_SETTINGS_MODULE=settings PYTHONPATH=../ python ./manage.py runserver 8777



# Старое


## Запуск detection unit

    PYTHONPATH=./src/ python src/detection/cli.py run --input=0

Пример запуска в продакшене:

    MONGODB_CONNECTION=mongodb://localhost PYTHONPATH=./src python  src/detection/cli.py run -i "rtsp://192.168.1.110:554/user=admin&password=***&channel=1&stream=0.sdp" --resize=1000  --forever=yes

## Запуск recognition unit

    PYTHONPATH=. celery -A recognition.tasks worker --pool=eventlet --loglevel=debug --concurrency=1


## Запуск api unit

    PYTHONPATH=. hug -f localapi/app.py --host=localhost -ma


## Запуск mongoDB**

    docker run --name some-mongo --rm -p 27017:27017 mongo


## Импортировать картинки

    PYTHONPATH=./src/ python src/core/cli.py load_images_from_directory ./initial-data/photos


# Запуск в докер-контейнерах

Не работает для внутренней или usb-камеры на маке.

## 1. Собрать образ

	docker build -f Dockerfile -t recognition-suite  .

## 2. Поправить переменные окружения 

В docker-compose.yml поправить переменные, например VIDEO_SOURCE

## 3. Запустить контейнеры

    docker-compose run
    
    
# TODO

## Улучшение распознавания

 - сделать align для лиц, пример - http://cmusatyalab.github.io/openface/usage/ или https://github.com/GaoGaoshu/mtcnn-align-crop
 - использовать amazon rekognition или решение от мейла

## Для демонстрации

Показать определение лиц на видеороликах?

 - https://www.youtube.com/watch?v=LHHDDqudKf8 - промо-видео
 - https://www.youtube.com/watch?v=pkHCeEZ-GPQ
 
## На что смотреть

 - https://www.deepvideoanalytics.com/ 
 - https://github.com/cmusatyalab/openface
 - https://github.com/davidsandberg/facenet
 
 
 # Разное
 
- Компания Ford недавно заявила, что не видит смысла в автомобилях третьего и четвертого уровня автономности – за ними все равно нужно следить, но из-за монотонности процесса водитель за рулем засыпает и подвергает себя опасности. По этой причине дочерней компании Ford, которая называется Argo AI, и которая занимается созданием искусственного интеллекта для автомобилей, были выделены деньги на постройку полностью беспилотного авто. Проект рассчитан на пять лет, а общие инвестиции составят один миллиард долларов. Рабочий прототип беспилотника должен появиться в 2021 году, а готовый к производству автомобиль – в 2025-ом.


# Адреса камер

 - Локальная камера hivision: rtsp://admin:admin12345@192.168.88.59/Streaming/Channels/101
 - Медофис:  rtsp://root:<password>@172.17.4.162/axis-media/media.amp


# API

## Swagger

Документация в swagger: https://vision-api.invitronet.ru/recognition/swagger.json

## Список лиц

Получить список лиц за последнее время:

    GET https://vision-api.invitronet.ru/recognition/presence/workstation/faces?workstation_id=196e356d-368b-e811-80d1-00155d52244a&minutes=2

Параметры:

    * `workstation_id` - идентификатор рабочего места АРМ МО. Если к этому рабочему месту камера не 'прикреплена', то метод возвратит http-статус 410.
    * `minutes` - интервал времени, за который нужно выдать список найденных лиц. По-умолчанию 1 минута.

Пример выдачи:

    {
        "faces": [
            {
                "face_id": 3295,                               // внутренний индентификатор лица в vision-api
                "face_url": "/recognize/face/image?id=3295",   // ссылка на изображение лица
                "last_seen_at": "2018-10-28T16:52:54.777Z"     // когда видели лицо последний раз
                "arm_guid": "0b504fa5-baa7-447e-8161-1028b4c72cb5"  // гуид АРМ, если установлен
            },
            ...
       ]
    }


## Установить гуид АРМ для лица

Назначить лицу гуид контакта:

    POST /recognition/recognize/face/set-id?face_id=3295&provider_name=arm_guid&provider_id=0b504fa5-baa7-447e-8161-1028b4c72cb5&workstation_id=2eff2fb5-6aea-4919-8f4a-bd6334b63f80&minutes=2

Параметры:

    * `face_id` - внутренний идентификатор лица
    * `provider_name` - тип идентификатора, константа, должно быть равно `arm_guid`
    * `provider_id` - собственно гуид
    * `workstation_id`  - идентификатор рабочей станции, с которой отправляется запрос


## Получить картинку лица

    GET /recognition/recognize/face/image?id=520&workstation_id=2eff2fb5-6aea-4919-8f4a-bd6334b63f80

Параметры:

    * `face_id` - внутренний идентификатор лица
    * `workstation_id`  - идентификатор рабочей станции, с которой отправляется запрос



https://vision-api.invitronet.ru/recognition/presence/workstation/faces.html?workstation_id=196e356d-368b-e811-80d1-00155d52244a&minutes=600&seen_times=2

Конкретное лицо:
https://vision-api.invitronet.ru/recognition/recognize/face/image?id=520


# Использование виджета:

1. Нужен jquery. Если еще не подключен, можно включить так:

    <script src="https://yastatic.net/jquery/3.1.1/jquery.min.js">

2. Загрузка кода виджета:

    <link href="https://vision-api.invitronet.ru/recognition/ui/faceid/1/widget.css" rel="stylesheet" />
    <script src="https://vision-api.invitronet.ru/recognition/ui/faceid/1/widget.js"></script>


3. Включение виджета:

    // Разместить в теле html-документа, точное место пока не важно:
    <div id="faceid-widget-placeholder"></div>

    // Где-нибудь в конце документа вызвать:
    <script type="text/javascript">
    $(document).ready(function(){
        var workstation_id = '<guid>'; // гуид рабочей станции, для привязки к камере
        faceid_widget.init('#faceid-widget-placeholder', workstation_id); // пока у init два параметра, потом будет больше
    });
    </script>
