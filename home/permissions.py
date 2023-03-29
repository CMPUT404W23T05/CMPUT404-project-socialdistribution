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
            token = None
    except User.DoesNotExist:
        user = None
        token = None



class RemoteAuth(BasePermission):

    token = get_anon_user()
    
    def has_permission(self, request, view):
        print(self.token)
        if str(request.auth) == self.token:
            print(True)
            return True
        else:
            return False

class CustomIsAuthenticated(IsAuthenticated):
    token = get_anon_user()
    
    def has_permission(self, request, view):
        print(self.token)
        if not super().has_permission(request, view):
            return False

        if request.auth and str(request.auth) == token:
            return False
        return True

