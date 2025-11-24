import os

from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from accounts.models import User

# 加载 .env 文件中的环境变量
load_dotenv()

class Command(BaseCommand):
    help = 'Create a platform admin'

    def handle(self, *args, **options):
        email = os.getenv('PLATFORM_ADMIN_EMAIL', None)
        phone = os.getenv('PLATFORM_ADMIN_PHONE', '10000000000')
        username = os.getenv('PLATFORM_ADMIN_USERNAME', 'Default_platform_admin')
        password = os.getenv('PLATFORM_ADMIN_PASSWORD', '123456')

        User.objects.create_platform_admin(
            email=email,
            phone=phone,
            username=username,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f'Platform admin {email} created successfully.'))