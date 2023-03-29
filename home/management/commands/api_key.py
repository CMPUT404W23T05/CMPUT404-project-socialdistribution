from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Creates a token for anonymous user'

    def handle(self, *args, **options):
        # Get or create the anonymous user
        anonymous_user, _ = User.objects.get_or_create(username='anonymous')

        # Create or update the token
        token, _ = Token.objects.get_or_create(user=anonymous_user)

        # Print the token
        print(f'Token: {token.key}')

