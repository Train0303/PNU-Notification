from .base import *

import pymysql

pymysql.install_as_MySQLdb()

# 설정한 도메인만 가능하도록 변경
ALLOWED_HOSTS = ['*']
DEBUG = False

MYSQL_USER = get_secret("MYSQL_USER")
MYSQL_PW = get_secret("MYSQL_PASSWORD")
MYSQL_HOST = get_secret("MYSQL_HOST")
ADMIN_EMAIL = get_secret("ADMIN_EMAIL")
ADMIN_PW = get_secret("ADMIN_PW")

# 향후 운영단계에서의 디비는 mysql로 전환할 예정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pnu_noti',
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PW,
        'HOST': MYSQL_HOST,
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4'
        }
    },
}