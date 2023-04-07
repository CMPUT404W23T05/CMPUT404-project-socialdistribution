from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import RemoteToken


class RemoteAuth(BasePermission):

    def get_anon_user(self):
        try:
            user = User.objects.get(username='anonymous')

            try:
                token = Token.objects.get(user=user)
                return token.key
            except Token.DoesNotExist:
                return None
        except User.DoesNotExist:
            return None

    def has_permission(self, request, view):
        anon_token = self.get_anon_user()
        if request.auth and str(request.auth) == str(anon_token):
            return True
        remote_token = RemoteToken.objects.filter(token=str(request.auth))
        if remote_token.exists():
            return True
        else:
            return False

class CustomIsAuthenticated(IsAuthenticated):

    def get_anon_user(self):
        try:
            user = User.objects.get(username='anonymous')

            try:
                token = Token.objects.get(user=user)
                return token.key
            except Token.DoesNotExist:
                return None
        except User.DoesNotExist:
            return None
    
    def has_permission(self, request, view):
        anon_token = self.get_anon_user()
        if not super().has_permission(request, view):
            return False

        if request.auth and str(request.auth) == str(anon_token):
            return False
        remote_token = RemoteToken.objects.filter(token=str(request.auth))
        if remote_token.exists():
            return False
        return True

