import requests
from django.core.management import BaseCommand, CommandError

from steam.models import GameList

GET_GAME_LIST_URL = "http://api.steampowered.com/ISteamApps/GetAppList/v2"


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(GET_GAME_LIST_URL)
        res = requests.get(GET_GAME_LIST_URL)

        if res.status_code != 200:
            print("get game list error: {}".format(res.status_code))
            raise CommandError(res.content.decode(encoding='utf-8'))

        game_list = GameList.objects.first()
        if game_list:
            game_list.data = res.json()["applist"]
        else:
            game_list = GameList(data=res.json()["applist"])
        game_list.save()
