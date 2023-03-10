from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return super().create_user(username=email, email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # superuser는 이메일 인증이 필요 없습니다.
        return super().create_superuser(username=email, email=email, password=password, **extra_fields)
