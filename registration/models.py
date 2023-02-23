from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(verbose_name="이메일", unique=True)
    username = models.CharField(unique=False, max_length=200)
    date_joined = models.DateTimeField(verbose_name="생성일", default=timezone.now)
    is_active = models.BooleanField(verbose_name="이메일인증여부", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        db_table = 'customuser'