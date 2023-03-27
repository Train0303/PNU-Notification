from datetime import datetime

from django.db import models
from django.utils import timezone


# Create your models here.
class Notice(models.Model):
    rss_link = models.URLField(verbose_name="RSS 링크", null=False, unique=True)
    updated_at = models.DateTimeField(verbose_name="최근 실행일", default=timezone.now)

    class Meta:
        db_table = "notice"
        ordering = ['updated_at']

    def is_valid(self, pub_date: datetime):
        if self.updated_at < pub_date:
            return True
        return False

    def __str__(self):
        return f"{self.rss_link}"


class HakjisiNotice(models.Model):
    notice_link = models.URLField(verbose_name="공지사항 링크", null=False, unique=True)
    title = models.CharField(verbose_name="공지사항 이름", max_length=128, null=False)
    last_notice_id = models.IntegerField(verbose_name="마지막 공지 id", null=False, default=0)

    class Meta:
        db_table = "notice_hakjisi"

    def __str__(self):
        return f"{self.title}"