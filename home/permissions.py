from rest_framework.permissions import BasePermission



class RemoteAuth(BasePermission):

    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token == 'Token itQmiFiX.HVJyCDX61EIHHjWRYm5naspa204iMrQA':
            return True
        else:
            return False
