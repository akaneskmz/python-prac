from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from steam.models import Achievement


class IndexView(ListView):
    template_name = "steam/index.html"
    queryset = Achievement.objects.filter(achieved=True).order_by('-unlock_time')
