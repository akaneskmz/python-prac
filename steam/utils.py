import io
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont

from steam.models import Achievement

STEAM_APP_DETAILS_URL = "http://store.steampowered.com/api/appdetails"


def get_app_details(appids: int, cc="us") -> dict:
    """ゲーム詳細情報取得"""
    params = {"appids": appids, "cc": cc}
    res = requests.get(STEAM_APP_DETAILS_URL, params)

    if res.status_code != 200:
        print("get apps details error: {}, {}".format(appids, res.status_code))
        return {}

    detail = res.json().get(str(appids))

    if not detail["success"]:
        print("get apps details error: {}, {}".format(appids, detail))
        return {}

    return detail.get("data")


def achieve_unlock_tweet(last_unlock_time):
    """実績解除ツイート"""

    # 新規実績
    new_achieve = Achievement.objects.filter(unlock_time__gte=datetime.fromtimestamp(last_unlock_time))

    if new_achieve:
        print(new_achieve)
        achieve_num = len(new_achieve)
        im = Image.new("RGB", (950, 78 * achieve_num), (11, 19, 23))
        draw = ImageDraw.Draw(im)
        name_font = ImageFont.truetype('./steam/fonts/meiryob003.ttf', 18)
        description_font = ImageFont.truetype('./steam/fonts/meiryo003.ttf', 12)
        games = [key for key, item in dict.fromkeys([a.app.name for a in new_achieve]).items()]
        print(games)
        for i, achieve in enumerate(new_achieve):
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

        im.show()
