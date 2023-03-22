import asyncio
import time
from typing import *

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from notice.crawl_hakjisi import get_hakjisi_notice, get_univ_notice
from notice.models import HakjisiNotice
from subscribe.models import HakjisiSubscribe


@sync_to_async
def get_user_subscribes(notice: HakjisiNotice):
    qs: List[HakjisiSubscribe] = list(HakjisiSubscribe.objects.filter(is_active=True, notice=notice)
                               .select_related('user', 'notice'))
    return qs


@sync_to_async
def reject_subscribe_email(failed_user: Set[str]):
    HakjisiSubscribe.objects.filter(user__email__in=list(failed_user)).update(is_active=False)


@sync_to_async
def set_notice_recent_id(notice: HakjisiNotice, max_id: int):
    notice.last_notice_id = max_id
    notice.save()


async def send_mail_async(send_mail_data):
    return send_mail(**send_mail_data)


def get_message(user_subscribe: HakjisiSubscribe, valid_item: dict):
    return f"""게시글 링크: {valid_item.get('notice_link')}
공지사항 링크: {user_subscribe.notice.notice_link}"""


async def send_hakjisi_to_user(notice: HakjisiNotice):
    """
    학생지원시스템(학생지원시스템 공지, 대학공지)의 새로운 공지사항을 사용자에게 메일로 전송합니다.
    get_xx_notice 함수를 통해 크롤링을 동작하여, 각 공지사항의 최대 id값과, 그 내용들을 받아올 수 있습니다.
    """
    current_id = notice.last_notice_id

    if notice.title == "학지시공지":
        max_id, contexts = get_hakjisi_notice(current_id=current_id)

    elif notice.title == "대학공지": # 대학 공지
        max_id, contexts = get_univ_notice(current_id=current_id)

    else:
        return

    await set_notice_recent_id(notice, max_id)

    user_subscribes: List[HakjisiSubscribe] = await get_user_subscribes(notice)

    failed_mail_users = set()
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

        failed_mail_users.update([task for task in await asyncio.gather(*tasks) if task != 1])

    if failed_mail_users:
        await reject_subscribe_email(failed_mail_users)


class Command(BaseCommand):
    """
    30분마다 `send_hakjisi_to_user` 함수를 동작시켜 내부적으로 크롤링을 실시하고,
    추가 공지사항이 있다면 사용자에게 메일을 보내는 방식입니다.
    Crontab으로 동작합니다.
    """

    def handle(self, *args: Any, **options: Any) -> NoReturn:
        start_time = time.time()

        notices = HakjisiNotice.objects.all()[:]  # [hakjisi, univ]
        loop = asyncio.get_event_loop()
        tasks = list(map(lambda x: asyncio.ensure_future(send_hakjisi_to_user(x)), notices))
        if tasks:
            loop.run_until_complete(asyncio.wait(tasks))

        print("Total Execute Time = ", time.time() - start_time, "s")