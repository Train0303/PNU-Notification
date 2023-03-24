from django.core.management.base import BaseCommand

from notice.crawl_hakjisi import get_hakjisi_notice, get_univ_notice
from notice.models import HakjisiNotice


hakjisi_url = 'https://onestop.pusan.ac.kr/page?menuCD=000000000000386'
univ_url = 'https://www.pusan.ac.kr/kor/CMS/Board/PopupBoard.do?mgr_seq=3&mode=list'

class Command(BaseCommand):
    def handle(self, *args, **options):

        hakjisi, hakjisi_created = HakjisiNotice.objects.get_or_create(
            notice_link=hakjisi_url,
            defaults={
                'title': '학지시공지',
                'last_notice_id': 0
            })

        univ, univ_created = HakjisiNotice.objects.get_or_create(
            notice_link=univ_url,
            defaults={
                'title': '대학공지',
                'last_notice_id': 0
            })

        # 테이블이 처음 만들어졌다면, 한번 크롤링을 진행하여 ID를 최신으로 만들어준다.
        if hakjisi_created:
            max_id, contexts = get_hakjisi_notice(current_id=0)
            hakjisi.last_notice_id = max_id
            hakjisi.save()

        if univ_created:
            max_id, contexts = get_univ_notice(current_id=0)
            univ.last_notice_id = max_id
            univ.save()
