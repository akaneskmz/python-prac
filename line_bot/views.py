from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    def post(self, request, *args, **kwargs):
        print(request.POST)
        return HttpResponse("OK")
