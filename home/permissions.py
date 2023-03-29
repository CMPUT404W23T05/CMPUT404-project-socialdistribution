from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User



class RemoteAuth(BasePermission):
    token = '1d2e3d4d55453d6da3cc618e7d83f3099e7b70e8'

    def has_permission(self, request, view):
        # print(str(request.auth) == self.token)
        if str(request.auth) == self.token:
            print(True)
            return True
        else:
            return False

class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if request.auth and str(request.auth) == '1d2e3d4d55453d6da3cc618e7d83f3099e7b70e8':
            return False
        return True

