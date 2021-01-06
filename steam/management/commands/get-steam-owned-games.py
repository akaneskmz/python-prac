import json
import os
import random

import requests
from django.core.management import BaseCommand, CommandError

from steam.constants import INVALID_APPS
from steam.models import OwnedGames, GameList
from steam.utils import get_app_details

STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")
GET_OWNED_GAMES_URL = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json"
API_COUNT_MAX = 50


class Command(BaseCommand):
    def handle(self, *args, **options):
        # API使用回数
        api_count = 0

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

        for owned_game in random.sample(owned_games["games"], len(owned_games["games"])):
            game_data = get_owned_game_old(owned_game["appid"])
            game_data.update(owned_game)

            appid = game_data["appid"]

            # ゲーム名追加
            if not game_data.get("name"):
                game_data["name"] = get_app_name(appid)

            # 詳細情報取得
            if not game_data.get("name") or not game_data.get("header_image") or not game_data.get(
                    "developers") or not game_data.get("publishers") or not game_data.get("price_overview"):
                if game_data["appid"] in INVALID_APPS:
                    game_data["header_image"] = INVALID_APPS[appid].get("header_image")
                    game_data["developers"] = INVALID_APPS[appid].get("developers")
                    game_data["publishers"] = INVALID_APPS[appid].get("publishers")
                    game_data["price_overview"] = INVALID_APPS[appid].get("price_overview")
                elif api_count < API_COUNT_MAX:
                    app_details = get_app_details(appid)
                    api_count += 1
                    if app_details:
                        game_data["name"] = app_details.get("name")
                        game_data["header_image"] = app_details.get("header_image")
                        game_data["developers"] = app_details.get("developers")
                        game_data["publishers"] = app_details.get("publishers")
                        # 価格があれば取得
                        if app_details.get("price_overview"):
                            price_overview = {key: app_details.get("price_overview").get(key) for key in
                                              ["currency", "initial"]}
                            game_data["price_overview"] = price_overview

            new_owned_games["games"].append(game_data)

        # データ保存
        print(f"API remains: {API_COUNT_MAX - api_count}")
        print(f"size: {len(json.dumps(new_owned_games))}")
        if own:
            own.data = new_owned_games
        else:
            own = OwnedGames(data=new_owned_games)

        own.save()
