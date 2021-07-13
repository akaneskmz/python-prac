import io
import os
import re
import threading
from base64 import b64encode

import requests
from PIL import Image
from bs4 import BeautifulSoup
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests_oauthlib import OAuth1

from kindle_share.models import KindleShare

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

TWITTER_MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWITTER_STATUS_UPDATE_URL = "https://api.twitter.com/1.1/statuses/update.json"


class AddView(View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        content = request.body.decode()
        KindleShare(add_date=timezone.now(), content=content).save()

        # ツイート処理を別スレッドで実行
        t = threading.Thread(target=share)
        t.start()

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddView, self).dispatch(*args, **kwargs)


lock = threading.Lock()


def share():
    lock.acquire()

    try:
        auth = OAuth1(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        for data in KindleShare.objects.filter(share_date__isnull=True):
            lines: str = data.content.split("\n\n")
            if "おすすめ" in lines[0]:
                # おすすめ
                title = lines[1]
                url = re.search(r"http.+", lines[2]).group()

                res_amazon = requests.get(url, headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64"})
                # print(res_amazon.content)
                soup = BeautifulSoup(res_amazon.text, "html.parser")
                image_url = soup.find_all('meta', property='og:image')[0]['content']

                # 画像取得
                image_res = requests.get(image_url)
                temp_io = io.BytesIO()
                temp_io.write(image_res.content)
                image_im = Image.open(temp_io)

                # 画像一時保存
                fp = io.BytesIO()
                image_im.save(fp, format="PNG")
                image_data = fp.getvalue()

                # 画像アップロード
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                params = {"media_data": b64encode(image_data)}
                res = requests.post(TWITTER_MEDIA_UPLOAD_URL, headers=headers, data=params, auth=auth)
                if res.status_code != 200:
                    print(f"media upload error: {res.status_code} {res.text}")
                    return False

                media_id = res.json()["media_id"]
                print(media_id)
                comment = "この本を読み終えました。"
                other_length = len(comment) + 1 + 12
                title_length = 140 - other_length
                status = f"{comment}\n{title[:title_length-1] + '…' if len(title) > title_length else title}\n{url}"
                tweet_params = {
                    'status': status,
                    'media_ids': media_id}
                tweet_res = requests.post(TWITTER_STATUS_UPDATE_URL, params=tweet_params, auth=auth)
                if tweet_res.status_code != 200:
                    print(f"tweet error: {tweet_res.status_code} {tweet_res.text}")
                    return False
            else:
                continue

            # ツイート済
            data.share_date = timezone.now()
            data.save()
    finally:
        lock.release()
