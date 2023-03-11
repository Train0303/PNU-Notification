FROM python:3.10.0

# MAINTAINER name
LABEL email="rjsdnxogh55@gmail.com"
LABEL name="PnuNotification"
LABEL version="0.1"
LABEL description="PnuNotification's Django Application"

ENV PYTHONUNBUFFERED=0
#ENV TZ=Asia/Seoul
ENV DJANGO_SETTINGS_MODULE=pnuNoti.settings.local

WORKDIR /app
ADD ./requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get update -qq
RUN apt-get install -y cron
