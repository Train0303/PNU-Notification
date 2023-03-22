# django import
from django.db import models

# other import
from registration.models import CustomUser
from notice.models import Notice, HakjisiNotice


# Create your models here.
class Subscribe(models.Model):
    title = models.CharField(verbose_name="구독명", max_length=128, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, null=False, related_name="notice_subscribe")
    notice_link = models.URLField(verbose_name="학과 공지사항 링크", null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscribe"
        verbose_name = "구독"
        verbose_name_plural = "구독 그룹"
        unique_together = ['user', 'notice', ]


class HakjisiSubscribe(models.Model):
    title = models.CharField(verbose_name="구독명", max_length=128, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    notice = models.ForeignKey(HakjisiNotice, on_delete=models.CASCADE, null=False, related_name="notice_hakjisisubscribe")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscribe_hakjisi"
        verbose_name = "학지시구독"
        verbose_name_plural = "구독 그룹"
        unique_together = ['user', 'notice', ]