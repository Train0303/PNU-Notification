from .base import *

ALLOWED_HOSTS = ["*"]
DEBUG = True

ADMIN_EMAIL = get_secret("ADMIN_EMAIL")
ADMIN_PW = get_secret("ADMIN_PW")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret("GMAIL_HOST")
EMAIL_HOST_PASSWORD = get_secret("GMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = "부산대학교 공지사항 알리미"+f" <{EMAIL_HOST_USER}>"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
