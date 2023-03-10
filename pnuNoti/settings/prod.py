from .base import *

import pymysql

pymysql.install_as_MySQLdb()

# 설정한 도메인만 가능하도록 변경
ALLOWED_HOSTS = ['pnunoti.site', 'www.pnunoti.site']
DEBUG = False

MYSQL_USER = get_secret("MYSQL_USER")
MYSQL_PW = get_secret("MYSQL_PASSWORD")
MYSQL_HOST = get_secret("MYSQL_HOST")
ADMIN_EMAIL = get_secret("ADMIN_EMAIL")
ADMIN_PW = get_secret("ADMIN_PW")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.daum.net'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = get_secret("EMAIL_HOST")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pnu_noti',
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PW,
        'HOST': MYSQL_HOST,
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
}