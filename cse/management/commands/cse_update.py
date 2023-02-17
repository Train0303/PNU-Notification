# django import
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

# model import
from cse.models import CseNotice

# command utils import
# from cse.management.utils import rss_list

# others import
from typing import *
from requests import get, Response
import xmltodict


class Command(BaseCommand):
    help = '정보컴퓨터공학부 공지사항 확인용입니다.'

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        response: Response = get(url='https://cse.pusan.ac.kr/bbs/cse/2605/rssList.do',
                                 params={"row": 5})

        if not response.ok:
            print(response.status_code)
            raise Exception("통신에러")

        items: List(dict) = xmltodict.parse(response.text)['rss']['channel']['item']
        items.reverse()
        for item in items:
            link = item.get('link')
            input_data = {
                'title': item.get('title'),
                'pub_date': item.get('pubDate'),
                'author': item.get('author')
            }
            cse_notice, created = CseNotice.objects.get_or_create(link=link,
                                                                  defaults=input_data)

            if created:
                html_response: Response = get(url=cse_notice.link)
                send_mail(subject=cse_notice.title,
                          message="새로운 공지사항이 등록되었습니다.",
                          from_email=settings.EMAIL_HOST,
                          recipient_list=["rjsdnxogh55@gmail.com"],
                          html_message=html_response.text,
                          fail_silently=False)
