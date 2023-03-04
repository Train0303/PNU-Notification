from .base import *

# 설정한 도메인만 가능하도록 변경
ALLOWED_HOSTS = ['*']
DEBUG = False

# 향후 운영단계에서의 디비는 mysql로 전환할 예정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}