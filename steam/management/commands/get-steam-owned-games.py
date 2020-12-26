import os

import requests
from django.core.management import BaseCommand, CommandError

from steam.constants import INVALID_APPS
from steam.models import OwnedGames, GameList
from steam.utils import get_app_details

STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")
GET_OWNED_GAMES_URL = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json"


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 所持ゲーム取得
        print(GET_OWNED_GAMES_URL)
        res = requests.get(GET_OWNED_GAMES_URL.format(STEAM_API_KEY, STEAM_ID))

        if res.status_code != 200:
            print("get owned games error: {}".format(res.status_code))
            raise CommandError(res.content.decode(encoding='utf-8'))

        # ゲームリスト
        game_list = GameList.objects.first()
        if game_list:
            apps = game_list.data["apps"]
        else:
            apps = []
        # print(apps)

        def get_app_name(app_id):
            """appidからゲーム名取得"""
            # APIで取得できないゲーム
            if app_id in INVALID_APPS:
                return INVALID_APPS[app_id].get("name")

            for app in apps:
                if app["appid"] == app_id:
                    return app["name"]
            app_detail = get_app_details(app_id)
            if app_detail.get("name"):
                return app_detail["name"]
            return None

        # 保存済みリスト取得
        own = OwnedGames.objects.first()
        if own:
            owned_games_old = own.data["games"]
        else:
            owned_games_old = []
        # print(owned_games_old)

        def get_owned_game_old(app_id):
            """appidから保存済みのゲームデータ取得"""
            for game in owned_games_old:
                if game["appid"] == app_id:
                    return game
            return {}

        owned_games = res.json()["response"]
        print(owned_games)

        # 保存用データ作成
        new_owned_games = {"game_count": owned_games["game_count"], "games": []}

        for owned_game in owned_games["games"]:
            game_data = get_owned_game_old(owned_game["appid"])
            game_data.update(owned_game)

            # ゲーム名追加
            if not game_data.get("name"):
                game_data["name"] = get_app_name(game_data["appid"])

            new_owned_games["games"].append(game_data)

        # データ保存
        if own:
            own.data = new_owned_games
        else:
            own = OwnedGames(data=new_owned_games)

        own.save()
