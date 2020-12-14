import os

import requests
from django.core.management import BaseCommand, CommandError

from steam.models import OwnedGames

STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")
GET_OWNED_GAMES_URL = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json"


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(GET_OWNED_GAMES_URL)
        res = requests.get(GET_OWNED_GAMES_URL.format(STEAM_API_KEY, STEAM_ID))

        if res.status_code != 200:
            print("get owned games error: {}".format(res.status_code))
            raise CommandError(res.content.decode(encoding='utf-8'))

        own = OwnedGames.objects.first()
        if own:
            own.data = res.json()["response"]
        else:
            own = OwnedGames(data=res.json()["response"])
        own.save()
