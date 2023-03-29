from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.static import serve
from django.conf import settings


def handleVue404(request):
    '''Serve Vue.js app but return 404 status code, 404 page is handled by Vue.js'''
    response = serve(request, '/vue/index.html',
                     document_root=settings.STATIC_ROOT)
    response.status_code = 404
    return response
