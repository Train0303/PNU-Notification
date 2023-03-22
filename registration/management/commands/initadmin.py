from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from registration.models import CustomUser

User: CustomUser = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.filter(email__iexact=settings.ADMIN_ID)
        if len(user) == 0:
            email = settings.ADMIN_EMAIL
            password = settings.ADMIN_PW
            print('Creating account for %s' % (email))
            admin = User.objects.create_superuser(email=email, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
