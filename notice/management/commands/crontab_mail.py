# django import
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, get_connection
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Count, QuerySet

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
import traceback
from smtplib import SMTPRecipientsRefused
from collections import Counter

failed_mail_users = []


def custom_send_mail(send_mail_data):
    try:
        send_mail(**send_mail_data)
        return 1
    except SMTPRecipientsRefused as e:
        return -1


# @sync_to_async를 안해주면 장고는 비동기 db접속을 거부한다.
@sync_to_async
def get_user_subscribes(notice: Notice):
    qs: List[Subscribe] = list(Subscribe.objects.filter(is_active=True, notice=notice)
                               .select_related('user', 'notice'))
    return qs


@sync_to_async
def update_exec_time(notice: Notice, last_data_time: datetime):
    notice.updated_at = last_data_time
    notice.save()


def reject_subscribe_user(failed_users: List[int]):
    if failed_users:
        Subscribe.objects.filter(user_id__in=failed_users).update(is_active=False)


async def send_mail_async(send_mail_data):
    result = custom_send_mail(send_mail_data)
    return result


def get_message(user_subscribe, valid_item):
    if user_subscribe.notice_link:
        return f"""게시글 링크: {valid_item.get('link')}
공지사항 링크: {user_subscribe.notice_link}
작성시간: {valid_item.get('pubDate')}
작성자: {valid_item.get('author')}"""

    return f"""게시글 링크: {valid_item.get('link')}
작성시간: {valid_item.get('pubDate')}
작성자: {valid_item.get('author')}"""


def send_failed_message_to_admin(failed_notices: List[Notice]):
    send_data = f"발생 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    for notice in failed_notices:
        send_data += f"""'공지사항 ID': {notice.id}
'공지사항 링크': {notice.rss_link}
----------------------

"""

    send_mail_data = {
        'subject': 'crontab_mail에서 에러가 발생했습니다.',
        'message': send_data,
        'from_email': settings.DEFAULT_FROM_EMAIL_ADMIN,
        'connection': get_connection(backend=settings.EMAIL_BACKEND_ADMIN),
        'recipient_list': [admin[1] for admin in settings.ADMINS],
        'fail_silently': False
    }
    custom_send_mail(send_mail_data)


async def send_rss_to_user(notice: Notice):
    """
    특정 학과의 공지사항을 받아와 마지막 갱신 시간보다 뒤에 등록된 글들을 구독한 회원들에게 메일전송
    """
    try:
        response: Response = get(url=notice.rss_link, timeout=120)
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
        failed_user_set = set()
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
            failed_user_set.update([user_subscribes[i].user.id for i, task in
                                    enumerate(await asyncio.gather(*tasks)) if task == -1])

        if failed_user_set:
            failed_mail_users.extend(list(failed_user_set))

        if last_data_time != -1:
            await update_exec_time(notice, last_data_time)
        return -1

    except Exception as e:
        print(notice.rss_link)
        traceback.print_exc()
        return notice.id


class Command(BaseCommand):
    """
    특정 학과의 공지사항이 갱신되면 구독한 회원들에게 메일을 보내주는 로직
    Crontab으로 동작
    """
    help = '공지사항 이메일 전송입니다.'

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        notices = list(Notice.objects.all().order_by('id'))

        start_time = time.time()
        loop = asyncio.get_event_loop()
        results = []
        tasks = list(map(lambda x: asyncio.ensure_future(send_rss_to_user(x)), notices))
        if tasks:
            results = loop.run_until_complete(asyncio.gather(*tasks))

        if not settings.DEBUG:
            # 전송 실패한 사용자가 있는 지 확인
            if failed_mail_users:
                # 사용자가 수신 거부를 해 모든 메일이 거부된 경우만 자동 알림 비활성화를 해주는 로직
                failed_mail_users_count = Counter(failed_mail_users)
                failed_mail_users_subscribe_count: QuerySet = Subscribe.objects.values(
                    'user_id'
                ).filter(
                    user__in=list(failed_mail_users_count.keys())
                ).annotate(
                    subscribe_count=Count('user_id')
                )

                # values() 메소드는 모델 object가 아닌 dict으로 반환하기에 x['user_id']와 같이 dict으로 접근해야함
                reject_mail_users = list(
                    map(
                        lambda x: x['user_id'],
                        filter(
                            lambda x: failed_mail_users_count[x['user_id']] == x['subscribe_count'],
                            list(failed_mail_users_subscribe_count))
                    ))
                reject_subscribe_user(reject_mail_users)

            # SMTPRecipientsRefused 예외를 제외한 전송 실패가 발생 경우 운영자에게 메일을 보냄
            failed_results = set(list(filter(
                lambda x: x != -1,
                results
            )))

            if failed_results:
                failed_notices = list(filter(
                    lambda x: x.id in failed_results,
                    notices
                ))
                send_failed_message_to_admin(failed_notices)

        print("Total Execute Time = ", time.time() - start_time, "s")
