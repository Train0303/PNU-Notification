FROM python:3.10.0

# MAINTAINER name
LABEL email="rjsdnxogh55@gmail.com"
LABEL name="PnuNotification"
LABEL version="0.1"
LABEL description="PnuNotification's Django Application"

ENV PYTHONUNBUFFERED=0
ENV PATH=~/.local/bin:$PATH
ENV TZ=Asia/Seoul
ENV DJANGO_SETTINGS_MODULE=pnuNoti.settings.local

WORKDIR /app
ADD ./requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ADD ./config/sh/cron.sh /
# RUN chmod +x /cron.sh

# ADD ./config/sh/userCron.sh /
# RUN chmod +x /userCron.sh

RUN apt-get update
RUN apt-get update -qq
RUN apt-get install -y libxml2-utils
