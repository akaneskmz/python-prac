import io
from urllib.parse import unquote

from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse

# Create your views here.
from django.views import View
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


class AltImageView(View):
    """代替画像"""
    def get(self, request, *args, **kwargs):
        title = unquote(kwargs.get("title"))

        im = Image.new("RGB", (460, 215), (128, 128, 128))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype('./steam/fonts/meiryo003.ttf', 48)
        draw.multiline_text((0, 0), title, fill=(0, 0, 0), font=font)

        output = io.BytesIO()
        im.save(output, format="PNG")
        return HttpResponse(output.getvalue(), content_type='image/png')
