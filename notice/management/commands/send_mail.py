# django import
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from asgiref.sync import sync_to_async

# model import
from notice.models import Notice

# others import
import asyncio
from typing import *
from requests import get, Response
import xmltodict
from datetime import datetime


@sync_to_async
def save_notice(notice: Notice):
    notice.updated_at = timezone.now()
    notice.save()


async def get_rss_data(notice: Notice):
    response: Response = get(url=notice.rss_link)
    res_xml: dict = xmltodict.parse(response.text)
    res_items: List[dict] = res_xml['rss']['channel']['item']
    res_filter = map(lambda x: {
                    'title': x['title'],
                    'link': x['link'],
                    'pubDate': datetime.strptime(x['pubDate'], '%Y-%m-%d %H:%M:%S.%f'),
                    'author': x['author']}, res_items)

    valid_items = filter(lambda x: notice.is_valid(x['pubDate']), res_filter)
    for valid_item in valid_items:
        print(valid_item)

    await save_notice(notice)


class Command(BaseCommand):
    help = '공지사항 이메일 전송입니다.'

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        rss_datas = Notice.objects.all()[:]
        loop = asyncio.get_event_loop()
        tasks = list(map(lambda x: asyncio.ensure_future(get_rss_data(x)), rss_datas))
        if tasks:
            loop.run_until_complete(asyncio.wait(tasks))
