# django import
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from asgiref.sync import sync_to_async
from django.conf import settings

# model import
from notice.models import Notice
from subscribe.models import Subscribe

# others import
import asyncio
from typing import *
from requests import get, Response
import xmltodict
from datetime import datetime
import time


@sync_to_async
def save_notice(notice: Notice):
    notice.updated_at = timezone.now()
    notice.save()


@sync_to_async
def get_user_subscribes(notice: Notice):
    qs: List[Subscribe] = list(Subscribe.objects.filter(is_active=True, notice=notice)
                               .select_related('user', 'notice'))
    return qs


async def send_rss_to_user(notice: Notice):
    start_time = time.time()
    response: Response = get(url=notice.rss_link)
    res_xml: dict = xmltodict.parse(response.text)
    res_items: List[dict] = res_xml['rss']['channel']['item']
    res_filter = map(lambda x: {
        'notice_title': x['title'],
        'link': x['link'],
        'pubDate': datetime.strptime(x['pubDate'], '%Y-%m-%d %H:%M:%S.%f'),
        'author': x['author']}, res_items)

    valid_items = list(filter(lambda x: notice.is_valid(x['pubDate']), res_filter))
    valid_items.reverse()

    user_subscribes: List[Subscribe] = await get_user_subscribes(notice)

    for valid_item in valid_items:
        valid_item['pubDate'] = valid_item['pubDate'].strftime("%Y-%m-%d %H:%M")
        for s in user_subscribes:
            send_mail_data = {
                'subject': f"{s.title}: {valid_item.get('notice_title')}",
                'message': f"""게시글 링크: {valid_item.get('link')}
작성시간: {valid_item.get('pubDate')}
작성자: {valid_item.get('author')}""",
                'from_email': settings.EMAIL_HOST,
                'recipient_list': [s.user.email],
                'fail_silently': False
            }
            send_mail(**send_mail_data)
            # print(send_mail_data['message'])
            # print(f"{s.title}/{s.user}/{s.notice.rss_link}")
    print(f"{notice.rss_link}'s Execute Time = ", time.time()-start_time)
    await save_notice(notice)


class Command(BaseCommand):
    help = '공지사항 이메일 전송입니다.'

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        rss_datas = Notice.objects.all()[:]
        start_time = time.time()
        loop = asyncio.get_event_loop()
        tasks = list(map(lambda x: asyncio.ensure_future(send_rss_to_user(x)), rss_datas))
        if tasks:
            loop.run_until_complete(asyncio.wait(tasks))

        print("Total Execute Time = ", time.time() - start_time, "s")
