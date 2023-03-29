from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def get_anon_user():
    try:
        user = User.objects.get(username='anonymous')

        try:
            token_obj = Token.objects.get(user=user)
            token = token_obj.key
            return token
        except Token.DoesNotExist:
            return '1d2e3d4d55453d6da3cc618e7d83f3099e7b70e8' #garbage token
    except User.DoesNotExist:
        user = None
        return '1d2e3d4d55453d6da3cc618e7d83f3099e7b70e8' #garbage token



class RemoteAuth(BasePermission):

    token = get_anon_user()
    
    def has_permission(self, request, view):
        if str(request.auth) == str(self.token):
            print(True)
            return True
        else:
            return False

class CustomIsAuthenticated(IsAuthenticated):
    token = get_anon_user()
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.auth and str(request.auth) == str(self.token):
            return False
        return True

