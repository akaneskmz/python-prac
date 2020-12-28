from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, TemplateView

from steam.models import Achievement, OwnedGames


class IndexView(ListView):
    template_name = "steam/index.html"
    queryset = Achievement.objects.filter(achieved=True).order_by('-unlock_time')


class OwnedGamesView(TemplateView):
    """所持ゲームリスト"""
    template_name = "steam/owned_games.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        owned_games = OwnedGames.objects.first()
        data = owned_games.data
        ctx["game_count"] = data["game_count"]

        sort_key = lambda x: x.get("name").upper() or ""
        ctx["games"] = sorted(data["games"], key=sort_key)
        return ctx
