from django.db import models
from django.utils import timezone

from datetime import datetime, timedelta


# Create your models here.
class Notice(models.Model):
    rss_link = models.URLField(verbose_name="RSS 링크", null=False, unique=True)
    updated_at = models.DateTimeField(verbose_name="최근 실행일", default=timezone.now)

    class Meta:
        db_table = "notice"
        ordering = ['updated_at']

    def is_valid(self, pub_date: datetime):
        ten_minutes_later = self.updated_at - timedelta(hours=10)
        if ten_minutes_later < pub_date:
            return True
        return False

    def __str__(self):
        return f"{self.rss_link}"
