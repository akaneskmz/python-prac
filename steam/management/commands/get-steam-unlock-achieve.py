import json
import os
from datetime import datetime

import requests
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from steam.models import App, Achievement

STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")
RECENTLY_URL = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={}&steamid={}&format=json"
SCHEMA_FOR_GAME_URL = "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={}&appid={}&l=japanese"
PLAYER_ACHIEVEMENTS_URL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/" \
                          "?appid={}&key={}&steamid={}&l=japanese"


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(RECENTLY_URL)
        res = requests.get(RECENTLY_URL.format(STEAM_API_KEY, STEAM_ID))

        if res.status_code != 200:
            print("recently error: {}".format(res.status_code))
            print(res.content.decode(encoding='utf-8'))
            return

        recently = json.loads(res.content)
        print(recently)

        for game in recently["response"]["games"]:
            print(game)
            try:
                app = App.objects.get(app_id=game["appid"])
            except App.DoesNotExist:
                app = App(app_id=game["appid"], name=game["name"])
                app.save()

            # プレイヤー実績取得
            res = requests.get(PLAYER_ACHIEVEMENTS_URL.format(game["appid"], STEAM_API_KEY, STEAM_ID))
            if res.status_code == 400:
                print(json.loads(res.content)["playerstats"]["error"])
                continue
            elif res.status_code != 200:
                print("achieve error: {}".format(res.status_code))
                print(res.content.decode(encoding='utf-8'))
                return

            player_stats = json.loads(res.content)["playerstats"]

            if "achievements" not in player_stats:
                print("no achievements")
                continue

            # ゲーム実績情報取得
            res = requests.get(SCHEMA_FOR_GAME_URL.format(STEAM_API_KEY, game["appid"]))
            print(res.content.decode(encoding='utf-8'))
            schemas = json.loads(res.content)["game"]["availableGameStats"]["achievements"]

            achievements = player_stats["achievements"]
            print(achievements)
            for achievement in achievements:
                try:
                    schema = [x for x in schemas if x["name"] == achievement["apiname"]][0]
                except IndexError:
                    schema = {}
                try:
                    achieve = Achievement.objects.get(app=app, api_name=achievement["apiname"])
                except Achievement.DoesNotExist:
                    achieve = Achievement(app=app, api_name=achievement["apiname"])
                achieve.name = achievement["name"]
                achieve.achieved = bool(achievement["achieved"])
                achieve.unlock_time = make_aware(datetime.fromtimestamp(achievement["unlocktime"]))
                achieve.description = achievement["description"]
                achieve.icon = schema.get("icon")
                achieve.hidden = bool(schema.get("hidden"))
                achieve.save()
