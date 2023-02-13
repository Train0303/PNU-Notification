from django.db import models


# Create your models here.
class CseNotice(models.Model):
    title = models.CharField(verbose_name="제목", max_length=100)
    link = models.URLField(verbose_name="공지 링크", unique=True)
    pub_date = models.DateTimeField(verbose_name="발행일")
    author = models.CharField(verbose_name="작성자", max_length=20)

    class Meta:
        ordering = ['-pub_date']
        db_table = "cse_notice"
