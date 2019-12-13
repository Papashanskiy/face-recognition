import os
import environ

root = environ.Path(__file__) - 3  # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env()  # reading .env file

SITE_ROOT = root()

DEBUG = env('DEBUG')  # False if not in os.environ
TEMPLATE_DEBUG = DEBUG

DATABASES = {'default': env.db(default='sqlite:////tmp/my-tmp-sqlite.db')}

SECRET_KEY = 'ke_r*79$hm0h=yw9t(i!%u36m0c)euvhipp$lkt22p^te-6$rq'  # env('SECRET_KEY')

ALLOWED_HOSTS = ['*']

RAVEN_CONFIG = {
    'dsn': 'http://f630cd98b66c4200a317da4dc49e5b98:5c8e92df04b541769e6455166cb91033@sv-mt06.invitro.ru/18',
}

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'face_recognition.recognitionapp',
    'face_recognition.presenceapp'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'


FACE_SIZE = (96, 96)
MINIMUM_FACE_SIZE = 100

MAILRU_CLIENT_ID = 'mcs3386719890.ml.vision.57WiPzVsWKPhqnehBUqUr'
MAILRU_CLIENT_SECRET = '6FhnZzG8oRg5Vrht7ovBvimcqnX3La28PKh3hvaSAJ4y9HVmHMjUBwf42oGzsD'
MAILRU_SERVICE_TOKEN = 'YRzjpxGGR2MWXZiHckBrEZm3cXaDXupjVpHvafqeWrzxrGShg'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


DEFAULT_DEVELOPER_WORKSTATION_ID = '3af81687-d28b-e711-80cb-00155d522421'

FAKE_WORKSTATION_ID1 = 'ffffffff-ffff-ffff-ffff-fffffffffff1'
FAKE_WORKSTATION_ID2 = 'ffffffff-ffff-ffff-ffff-fffffffffff2'


def FAKE_WORKSTATION_ID(num):
    return 'ffffffff-ffff-ffff-ffff-fffffffffff{}'.format(num)


CAMERAID_TO_WORKSTATION = {

    'NAG-1': {
        'workstation_id': '5c1ffec9-7fcb-e711-80ce-00155d522528',
        'location_name': 'Москва, Центральный медофис',
        'area_name': 'Ресепшен, 1',
        'min_photo_wh': 150 * 150
    },

    #'2': {
    #    'workstation_id': '07c2a9a5-65c4-4d67-b145-05f7b2ec5517',
    #    'location_name': 'Рязань, Ленина, 2',
    #    'area_name': ''
    #},

    'DEV-1': {
        'workstation_id': DEFAULT_DEVELOPER_WORKSTATION_ID,
        'location_name': 'Камера разработчиков',
        'area_name': 'Инвитро-ИТ'
    },

    # -- Реальные камеры

    'FRC-1': {
        'workstation_id': '9fb26e0b-e278-412a-a2f0-e0b37dd49999',
        'location_name': 'МО Одинцово, ИВАН-ОДИ-МК',
        'min_photo_wh': 80*80,
    },

    'FRC-3': {
        'workstation_id': '1b8e94e8-2250-4964-bc89-55007fbd7f4e',
        'location_name': 'ИВАН-МСК-МЛ. МО Молодежная',
        'min_photo_wh': 100 * 100
    },

    'FRC-4': {
        'workstation_id': 'af7c5820-f706-4468-aab8-9282a28cf7e5',
        'location_name': 'ИВАН-СРН-ВО. Саранск',
        'min_photo_wh': 100 * 100
    },

    'FRC-5': {
        'workstation_id': FAKE_WORKSTATION_ID1,
        'location_name': 'Дубровка-2 (КОЗЛОВ-ДУБ2)к',
        'min_photo_wh': 100 * 100
    },

    'FRC-6': {
        'workstation_id': FAKE_WORKSTATION_ID2,
        'location_name': 'Ессентуки-1 (РОМА-ЕСС-ОК)',
        'min_photo_wh': 40 * 40
    },

    'FRC-7': {
        'workstation_id': FAKE_WORKSTATION_ID1,
        'location_name': 'МЦ Марьина роща КОЗЛОВ-МР',
        'min_photo_wh': 40 * 40
    },

#    'FRC-8': {
#        'workstation_id': FAKE_WORKSTATION_ID(8),
#        'location_name': 'МО Дм.Донского',
#        'min_photo_wh': 40 * 40
#    },

    'FRC-9': {
        'workstation_id': FAKE_WORKSTATION_ID(9),
        'location_name': 'ФМО Ломоновоский проспект (ИВАН-МСК-МФ)',
        'min_photo_wh': 40 * 40
    },

    'FRC-11': {
        'workstation_id': '2ac160dd-1ace-4b10-b9e7-1de6bde1bded',
        'location_name': 'Бульвар Дмитрия Донского',
        'min_photo_wh': 40 * 40
    },

    'FRC-12': {
        'workstation_id': '21af4d33-4ea5-e811-80d1-00155d52244a',
        'location_name': 'МО МИХНЕВО, ИВАН-МСК-СВ',
        'min_photo_wh': 40 * 40
    },
    'FRC-13': {
        'workstation_id': 'b07935d9-0bb3-e711-80cc-00155d522528',
        'location_name': 'МО Восточное Дегунино. ИВАН-МСК-ЛТ',
    }
}

STATSD_CLIENT = 'django_statsd.clients.normal'
STATSD_HOST = '172.17.16.115'
STATSD_PREFIX = 'facerec.rec'
