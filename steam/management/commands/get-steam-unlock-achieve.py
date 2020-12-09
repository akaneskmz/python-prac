import json
import os

import requests
from django.core.management import BaseCommand

from steam.models import App

STEAM_API_KEY = os.environ.get("STEAM_API_KEY")
STEAM_ID = os.environ.get("STEAM_ID")
RECENTLY_URL = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={}&steamid={}&format=json"
PLAYER_ACHIEVEMENTS_URL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={}&key={}&steamid={}&l=japanese"

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
                App.objects.get(app_id=game["appid"])
            except App.DoesNotExist:
                app = App(app_id=game["appid"], name=game["name"])
                app.save()

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

            achievements = player_stats["achievements"]
            print(achievements)


# import pickle
# import time
# import math
# from datetime import datetime, timedelta

# PLAYER_ACHIEVEMENTS_URL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={0}&key={1}&steamid={2}&l=japanese"
# SCHEMA_FOR_GAME = "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={0}&appid={1}&l=japanese"
# DUMP_FILE = "/home/akaneskmz/www/get-steam-unlock-achieve.dump"
# IMG_DIR = "/home/akaneskmz/www/"
# CONVERT = "/usr/local/bin/convert"
# MONTAGE = "/usr/local/bin/montage"
#
# # ローカル実行用
# if os.name == "nt":
# 	DUMP_FILE = "D:\\dt\\www\\get-steam-unlock-achieve.dump"
# 	IMG_DIR = "D:\\dt\\www\\"
# 	CONVERT = "D:\\fs\\ImageMagick-7.0.7-9-portable-Q16-x64\\convert"
# 	MONTAGE = "D:\\fs\\ImageMagick-7.0.7-9-portable-Q16-x64\\montage"
#
# # 現在時刻
# now = datetime.now()
#
# # データ初期化
# dmp = {}
# if os.path.exists(DUMP_FILE):
# 	f = open(DUMP_FILE, 'r')
# 	dmp = pickle.load(f)
# 	f.close()
# else:
# 	dmp['lasttime'] = now + timedelta(days=-1)
# 	dmp['forrss'] = []
# lasttime = int(time.mktime(dmp['lasttime'].timetuple()))
# dmp['lasttime'] = now
#

#
# 	paAchieve = paData['playerstats']['achievements']
# 	newAchieve = [x for x in paAchieve if x['achieved']==1 and x['unlocktime'] > lasttime]
#
# 	# 実績未取得はスキップ
# 	if not newAchieve:
# 		continue
#
# 	forRssData = {}
# 	forRssData['time'] = now
# 	forRssData['appid'] = appid
# 	forRssData['game'] = gameName
#
# 	guid = str(int(time.mktime(now.timetuple()))) + "_" + str(appid)
# 	forRssData['guid'] = guid
#
# 	# ゲームの実績詳細情報を取得
# 	schemaJson = urllib2.urlopen(SCHEMA_FOR_GAME.format(API_KEY, appid)).read()
#
# 	schemaData = json.loads(schemaJson)
#
# 	achiDtl = schemaData['game']['availableGameStats']['achievements']
#
# 	forRssData['achieves'] = []
# 	cnt = 0
#
# 	for i in range(len(newAchieve)):
# 		ac = newAchieve[i]
# 		ad = [x for x in achiDtl if x['name'] == ac['apiname']][0]
# 		forRssData['achieves'].append({'name': ac['name'], 'desc': ad['description'] if 'description' in ad else '-'})
# 		urllib.urlretrieve(ad['icon'], IMG_DIR + "ac" + guid + "_" + str(i) + ".jpg")
# 		cnt += 1
# 		# print guid + "_" + str(i) + ".jpg"
#
# 	n = int(math.ceil((cnt+1)/12.0))
# 	w = int(math.ceil(math.sqrt(n))) * 4
# 	h = int(math.ceil(cnt/float(w)))
# 	os.system(MONTAGE + " " + IMG_DIR + "ac" + guid + "_* -tile " + str(w) + "x" + str(h) + " -geometry +0+0 " + IMG_DIR + "ac" + guid + ".jpg")
#
# 	dmp['forrss'].append(forRssData)
#
# #print dmp['forrss']
#
# f = open(DUMP_FILE, 'w')
# pickle.dump(dmp, f)
# f.close()
