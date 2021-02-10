import os

from django.http import HttpResponse, HttpResponseBadRequest

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

# 環境変数取得
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, StickerMessage

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


class IndexView(View):
    def post(self, request, *args, **kwargs):
        signature = request.headers['X-Line-Signature']
        print(signature)
        body = request.body.decode()

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("InvalidSignatureError")
            return HttpResponseBadRequest()

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
    print(f"event.reply_token = {event.reply_token}")
    print(f"event.message = {event.message}")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.sticker_id))