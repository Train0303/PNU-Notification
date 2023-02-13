# django import
from django.core.management.base import BaseCommand

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
                                 params={"row": 20})

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
                '이메일 보내기 코드'
