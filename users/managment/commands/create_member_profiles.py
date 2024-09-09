from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import MemberProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates MemberProfile for existing users'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            MemberProfile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created member profiles for existing users'))