import io
from math import ceil

import requests
from PIL import Image
from django.core.management import BaseCommand

from steam.models import OwnedGames


class Command(BaseCommand):
    def handle(self, *args, **options):
        owned_games = OwnedGames.objects.first()
        data = owned_games.data

        sort_key = lambda x: x.get("name").upper() or ""
        games = sorted(data["games"], key=sort_key)
        game_count = len(games)
        print(game_count)
        v_count = ceil(game_count / 20)
        print(v_count)

        im = Image.new("RGB", (92 * 20, 43 * v_count), (128, 128, 128))
        for i, game in enumerate(games):
            print(f'{i + 1} / {game_count}: {game["header_image"]}')
            header_url = game["header_image"] if game[
                "header_image"] else f'http://localhost:5000/steam/alt_image/{game["name"]}/'
            res = requests.get(header_url)
            temp_io = io.BytesIO()
            temp_io.write(res.content)
            header_im = Image.open(temp_io)
            header_resize_im = header_im.resize(size=(92, 43))
            im.paste(header_resize_im, (i % 20 * 92, int(i / 20) * 43))

        with open("./image.jpg", "wb") as fp:
            im.save(fp, format="JPEG")
