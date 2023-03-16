from .base import *

import pymysql

pymysql.install_as_MySQLdb()

# 설정한 도메인만 가능하도록 변경
ALLOWED_HOSTS = ['pnunoti.site', 'www.pnunoti.site']
CSRF_TRUSTED_ORIGINS = ['https://pnunoti.site', 'https://www.pnunoti.site']
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
DEFAULT_FROM_EMAIL = "부산대학교 공지사항 알리미"+f" <{EMAIL_HOST_USER}>"

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

MIDDLEWARE += [
    "pnuNoti.middleware.HealthCheckMiddleware",
]

# --------------- 배포환경이 ec2면 private IP를 ALLOWED_HOSTS에 추가 -------------------

def is_ec2_linux():
    """Detect if we are running on an EC2 Linux Instance
       See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
    """
    if os.path.isfile('/sys/hypervisor/uuid'):
        with open('/sys/hypervisor/uuid') as f:
            uuid = f.read()
            return uuid.startswith('ec2')
    return False

def get_linux_ec2_private_ip():
    """Get the private IP Address of the machine if running on an EC2 linux server"""
    from urllib.request import urlopen
    if not is_ec2_linux():
        return None
    try:
        response = urlopen('http://169.254.169.254/latest/meta-data/local-ipv4')
        ec2_ip = response.read().decode('utf-8')
        if response:
            response.close()
        return ec2_ip
    except Exception as e:
        print(e)
        return None


private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS.append(private_ip)