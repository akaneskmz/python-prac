import os
from base64 import b64encode

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from requests_oauthlib import OAuth1

from steam.models import LastScreenShots

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

STEAM_USER = os.environ.get("STEAM_USER")

LIST_URL = f"http://steamcommunity.com/id/{STEAM_USER}/screenshots/?appid=0&sort=newestfirst&browsefilter=myfiles&view=grid"
SCREENSHOT_URL = "http://steamcommunity.com/sharedfiles/filedetails/"
TWITTER_MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWITTER_STATUS_UPDATE_URL = "https://api.twitter.com/1.1/statuses/update.json"


class Command(BaseCommand):
    def handle(self, *args, **options):

        last_screen_shot = LastScreenShots.objects.first()
        if last_screen_shot:
            last_screen_shot_time = last_screen_shot.last_screen_shot_time
        else:
            last_screen_shot_time = 0

        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        list_res = requests.get(LIST_URL)
        list_soup = BeautifulSoup(list_res.content, "html.parser")
        profile_media_items = list_soup.find_all(class_="profile_media_item")
        for profile_media_item in reversed(profile_media_items):
            q = profile_media_item.select('.imgWallHoverDescription q')
            if q:
                title = q[0].text
            else:
                title = "(untitled)"

            node = profile_media_item.select('div.imgWallItem')
            node_id = node[0].attrs.get('id')
            item_id = int(node_id.replace('imgWallItem_', ''))
            if item_id > last_screen_shot_time:
                detail_res = requests.get(SCREENSHOT_URL, headers={'Accept-Language': 'ja,en-US'},
                                          params={'id': item_id})
                detail_soup = BeautifulSoup(detail_res.content, "html.parser")
                h3 = detail_soup.select("h3.apphub_responsive_menu_title")
                a = detail_soup.select("div.screenshotAppName a")
                game_title = h3[0].text if h3 else a[0].text
                print(game_title, title)

                img_link = detail_soup.select(".actualmediactn a")
                img_url = img_link[0].attrs.get("href")
                img_res = requests.get(img_url)
                data = img_res.content

                # 画像アップロード
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                params = {"media_data": b64encode(data)}
                res = requests.post(TWITTER_MEDIA_UPLOAD_URL, headers=headers, data=params, auth=auth)
                if res.status_code != 200:
                    print(f"media upload error: {res.text}")
                    return False

                media_id = res.json()["media_id"]
                print(media_id)
                tweet_params = {'status': f'[{game_title}] {title}', 'media_ids': media_id}
                tweet_res = requests.post(TWITTER_STATUS_UPDATE_URL, params=tweet_params, auth=auth)
                if tweet_res.status_code != 200:
                    print(f"tweet error: {res.text}")
                    return False

                if last_screen_shot:
                    last_screen_shot.last_screen_shot_time = item_id
                else:
                    last_screen_shot = LastScreenShots(last_screen_shot_time=item_id)
                last_screen_shot.save()
