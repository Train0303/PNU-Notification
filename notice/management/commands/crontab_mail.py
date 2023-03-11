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


# @sync_to_async를 안해주면 장고는 비동기 db접속을 거부한다.
@sync_to_async
def get_user_subscribes(notice: Notice):
    qs: List[Subscribe] = list(Subscribe.objects.filter(is_active=True, notice=notice)
                               .select_related('user', 'notice'))
    return qs


@sync_to_async
def reject_subscribe_email(failed_user: Set[str]):
    Subscribe.objects.filter(user__email__in=list(failed_user)).update(is_active=False)

@sync_to_async
def update_exec_time(notice: Notice, last_data_time: datetime):
    notice.updated_at = last_data_time
    notice.save()


async def send_mail_async(send_mail_data):
    return send_mail(**send_mail_data)


def get_message(user_subscribe, valid_item):
    if user_subscribe.notice_link:
        return f"""게시글 링크: {valid_item.get('link')}
공지사항 링크: {user_subscribe.notice_link}
작성시간: {valid_item.get('pubDate')}
작성자: {valid_item.get('author')}"""

    return f"""게시글 링크: {valid_item.get('link')}
작성시간: {valid_item.get('pubDate')}
작성자: {valid_item.get('author')}"""


async def send_rss_to_user(notice: Notice):
    """
    특정 학과의 공지사항을 받아와 마지막 갱신 시간보다 뒤에 등록된 글들을 구독한 회원들에게 메일전송
    """
    response: Response = get(url=notice.rss_link)
    res_xml: dict = xmltodict.parse(response.text)
    res_items: List[dict] = res_xml['rss']['channel']['item']
    res_filter = map(lambda x: {
        'notice_title': x['title'],
        'link': x['link'],
        'pubDate': datetime.strptime(x['pubDate'], '%Y-%m-%d %H:%M:%S.%f'),
        'author': x['author']}, res_items)

    valid_items = list(filter(lambda x: notice.is_valid(x['pubDate']), res_filter))
    last_data_time = valid_items[0]["pubDate"] if valid_items else -1
    valid_items.reverse()

    user_subscribes: List[Subscribe] = await get_user_subscribes(notice)

    failed_mail_users = set()
    for valid_item in valid_items:
        valid_item['pubDate'] = valid_item['pubDate'].strftime("%Y-%m-%d %H:%M")
        tasks = []
        for s in user_subscribes:
            send_mail_data = {
                'subject': f"{s.title}: {valid_item.get('notice_title')}",
                'message': get_message(s, valid_item),
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'recipient_list': [s.user.email],
                'fail_silently': False
            }
            tasks.append(send_mail_async(send_mail_data))

        failed_mail_users.update([task for task in await asyncio.gather(*tasks) if task != 1])

    if failed_mail_users:
        await reject_subscribe_email(failed_mail_users)

    if last_data_time != -1:
        await update_exec_time(notice, last_data_time)

class Command(BaseCommand):
    """
    특정 학과의 공지사항이 갱신되면 구독한 회원들에게 메일을 보내주는 로직
    Crontab으로 동작
    """
    help = '공지사항 이메일 전송입니다.'

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        rss_datas = Notice.objects.all()[:]
        start_time = time.time()
        loop = asyncio.get_event_loop()
        tasks = list(map(lambda x: asyncio.ensure_future(send_rss_to_user(x)), rss_datas))
        if tasks:
            loop.run_until_complete(asyncio.wait(tasks))
        # Notice.objects.all().update(updated_at=timezone.now())
        print("Total Execute Time = ", time.time() - start_time, "s")
