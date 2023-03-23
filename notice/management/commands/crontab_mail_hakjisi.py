import asyncio
import time
from typing import *
from datetime import datetime
import traceback

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.core.management.base import BaseCommand

from notice.crawl_hakjisi import get_hakjisi_notice, get_univ_notice
from notice.models import HakjisiNotice
from subscribe.models import HakjisiSubscribe

from crontab_mail import custom_send_mail, send_mail_async, remove_duplication


@sync_to_async
def get_user_subscribes(notice: HakjisiNotice):
    qs: List[HakjisiSubscribe] = list(HakjisiSubscribe.objects.filter(is_active=True, notice=notice)
                               .select_related('user', 'notice'))
    return qs


@sync_to_async
def reject_subscribe_user(failed_users: List[int]):
    HakjisiSubscribe.objects.filter(user_id__in=failed_users).update(is_active=False)


@sync_to_async
def set_notice_recent_id(notice: HakjisiNotice, max_id: int):
    notice.last_notice_id = max_id
    notice.save()


def get_message(user_subscribe: HakjisiSubscribe, valid_item: dict):
    return f"""게시글 링크: {valid_item.get('notice_link')}
공지사항 링크: {user_subscribe.notice.notice_link}"""


def send_failed_message_to_admin(failed_notices: List[HakjisiNotice]):
    send_data = f"발생 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    for notice in failed_notices:
        send_data += f"""'공지사항 제목': {notice.title}
'공지사항 링크': {notice.notice_link}
----------------------

"""

    send_mail_data = {
        'subject': 'crontab_mail_hakjisi에서 에러가 발생했습니다.',
        'message': send_data,
        'from_email': settings.DEFAULT_FROM_EMAIL_ADMIN,
        'connection': get_connection(backend=settings.EMAIL_BACKEND_ADMIN),
        'recipient_list': [admin[1] for admin in settings.ADMINS],
        'fail_silently': False
    }
    custom_send_mail(send_mail_data)


async def send_hakjisi_to_user(notice: HakjisiNotice):
    """
    학생지원시스템(학생지원시스템 공지, 대학공지)의 새로운 공지사항을 사용자에게 메일로 전송합니다.
    get_xx_notice 함수를 통해 크롤링을 동작하여, 각 공지사항의 최대 id값과, 그 내용들을 받아올 수 있습니다.
    """
    current_id = notice.last_notice_id
    try:
        if notice.title == "학지시공지":
            max_id, contexts = get_hakjisi_notice(current_id=current_id)
        elif notice.title == "대학공지": # 대학 공지
            max_id, contexts = get_univ_notice(current_id=current_id)
        else:
            raise Exception(f"등록되지 않은 title입니다. {notice.title}")

        contexts = remove_duplication(contexts)

        await set_notice_recent_id(notice, max_id)

        user_subscribes: List[HakjisiSubscribe] = await get_user_subscribes(notice)

        failed_user_set = set()
        for context in contexts:
            tasks = []
            for s in user_subscribes:
                send_mail_data = {
                    'subject': f"{s.title}: {context.get('notice_title')}",
                    'message': get_message(s, context),
                    'from_email': settings.DEFAULT_FROM_EMAIL,
                    'recipient_list': [s.user.email],
                    'fail_silently': False
                }
                tasks.append(send_mail_async(send_mail_data))

            failed_user_set.update([user_subscribes[i].user.id for i, task in
                                    enumerate(await asyncio.gather(*tasks)) if task == -1])

        if failed_user_set:
            await reject_subscribe_user(list(failed_user_set))

    except Exception as e:
        print(notice.title)
        traceback.print_exc()
        return notice.id


class Command(BaseCommand):
    """
    30분마다 `send_hakjisi_to_user` 함수를 동작시켜 내부적으로 크롤링을 실시하고,
    추가 공지사항이 있다면 사용자에게 메일을 보내는 방식입니다.
    Crontab으로 동작합니다.
    """

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        notices = HakjisiNotice.objects.all().order_by('id')  # [hakjisi, univ]

        start_time = time.time()
        loop = asyncio.get_event_loop()
        results = []
        tasks = list(map(lambda x: asyncio.ensure_future(send_hakjisi_to_user(x)), notices))
        if tasks:
            results = loop.run_until_complete(asyncio.gather(*tasks))

        if not settings.DEBUG:
            # 지정한 예외를 제외한 전송 실패가 발생 경우 운영자에게 메일을 보냄
            failed_results = set(list(filter(
                lambda x: x != -1,
                results)))

            if failed_results:
                failed_notices = list(filter(
                    lambda x: x.id in failed_results,
                    notices))
                send_failed_message_to_admin(failed_notices)

        print("Total Execute Time = ", time.time() - start_time, "s")