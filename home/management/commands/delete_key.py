from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Deletes the anonymous user and token'

    def handle(self, *args, **options):
        # Get the anonymous user
        try:
            anonymous_user = User.objects.get(username='anonymous')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Anonymous user does not exist.'))
            return

        # Delete the token
        try:
            token = Token.objects.get(user=anonymous_user)
            token.delete()
        except Token.DoesNotExist:
            self.stdout.write(self.style.WARNING('Token does not exist.'))

        # Delete the user
        anonymous_user.delete()

        self.stdout.write(self.style.SUCCESS('Anonymous user and token deleted.'))
