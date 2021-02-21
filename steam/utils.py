import io
import os
from base64 import b64encode
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont
from requests_oauthlib import OAuth1

from steam.models import Achievement

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

STEAM_APP_DETAILS_URL = "http://store.steampowered.com/api/appdetails"
TWITTER_MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWITTER_STATUS_UPDATE_URL = "https://api.twitter.com/1.1/statuses/update.json"

TWEET_ACHIEVE_TAG = os.environ.get("TWEET_ACHIEVE_TAG")


def get_app_details(appids: int, ccs="jp,,us") -> dict:
    """ゲーム詳細情報取得"""
    for cc in ccs.split(","):
        params = {"appids": appids}
        if cc:
            params["cc"] = cc
        res = requests.get(STEAM_APP_DETAILS_URL, params)

        if res.status_code != 200:
            print("get apps details error: {}, {}, {}".format(appids, cc, res.status_code))
            continue

        detail = res.json().get(str(appids))

        if not detail["success"]:
            print("get apps details error: {}, {}, {}".format(appids, cc, detail))
            continue

        return detail.get("data")
    return {}


def achieve_unlock_tweet(last_unlock_time):
    """実績解除ツイート"""

    # 新規実績
    new_achieve = Achievement.objects.filter(unlock_time__gte=datetime.fromtimestamp(last_unlock_time))

    if new_achieve:
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        print(new_achieve)
        name_font = ImageFont.truetype('./steam/fonts/meiryob003.ttf', 18)
        description_font = ImageFont.truetype('./steam/fonts/meiryo003.ttf', 12)
        # ツイート用タグ
        tag = f"\n #{TWEET_ACHIEVE_TAG}" if TWEET_ACHIEVE_TAG else ""
        games = [key for key, item in dict.fromkeys([a.app for a in new_achieve]).items()]
        print(games)

        for game in games:
            sort_key = lambda x: x.unlock_time
            achieves = sorted([a for a in new_achieve if a.app == game], key=sort_key)

            # 実績数カウント
            achieve_num = len(achieves)
            achieve_num_current = Achievement.objects.filter(app=game, achieved=True).count()
            achieve_num_total = Achievement.objects.filter(app=game).count()
            # 進捗テキスト
            progress = f"{achieve_num_current}/{achieve_num_total}(+{achieve_num})"

            im = Image.new("RGB", (950, 78 * achieve_num), (11, 19, 23))
            draw = ImageDraw.Draw(im)
            for i, achieve in enumerate(achieves):
                offset_y = 78 * i
                # アイコン取得
                icon = requests.get(achieve.icon)
                temp_io = io.BytesIO()
                temp_io.write(icon.content)
                icon_im = Image.open(temp_io)
                # アイコン貼り付け
                im.paste(icon_im, (12, offset_y + 7))
                # 枠
                draw.rectangle((83, offset_y + 7, 938, offset_y + 71), fill=(8, 12, 17), width=0)

                draw.text((89, offset_y + 7 + 6), achieve.name, fill=(241, 241, 241), font=name_font)
                draw.text((89, offset_y + 7 + 30), achieve.description, fill=(137, 137, 137), font=description_font)
                unlock_time_text = "アンロックした日 " + datetime.strftime(achieve.unlock_time, "%Y年%m月%d日 %H時%M分")
                unlock_time_text_size = draw.textsize(unlock_time_text, font=description_font)
                draw.text((932 - unlock_time_text_size[0], offset_y + 7 + 25), unlock_time_text, fill=(137, 137, 137),
                          font=description_font)

            # 画像一時保存
            fp = io.BytesIO()
            im.save(fp, format="PNG")
            data = fp.getvalue()

            # 画像アップロード
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            params = {"media_data": b64encode(data)}
            res = requests.post(TWITTER_MEDIA_UPLOAD_URL, headers=headers, data=params, auth=auth)
            if res.status_code != 200:
                print(f"media upload error: {res.text}")
                return False

            media_id = res.json()["media_id"]
            print(media_id)
            tweet_params = {'status': f'{game.name}の実績を解除しました。{progress}{tag}', 'media_ids': media_id}
            tweet_res = requests.post(TWITTER_STATUS_UPDATE_URL, params=tweet_params, auth=auth)
            if tweet_res.status_code != 200:
                print(f"tweet error: {res.text}")
                return False

        # 正常終了
        return True
