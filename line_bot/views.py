import json
import os

from django.http import HttpResponse, HttpResponseBadRequest

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

# 環境変数取得
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, StickerMessage, TextMessage, TemplateSendMessage, \
    ButtonsTemplate, MessageAction, PostbackEvent

YOUR_CHANNEL_ACCESS_TOKEN = os.environ.get("YOUR_CHANNEL_ACCESS_TOKEN", "")
YOUR_CHANNEL_SECRET = os.environ.get("YOUR_CHANNEL_SECRET", "")

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


class IndexView(View):
    def post(self, request, *args, **kwargs):
        signature = request.headers['X-Line-Signature']
        body = request.body.decode()
        print(f"header = {request.headers}")
        print(f"body = {body}")

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
def handle_sticker_message(event):
    """スタンプメッセージへの返答"""
    print(f"event.reply_token = {event.reply_token}")
    print(f"event.message = {event.message}")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=json.dumps(json.loads(str(event.message)), indent=2)))
    # line_bot_api.push_message(event.source.user_id, TextSendMessage(text="push"))


@handler.add(PostbackEvent)
def handle_postback(event):
    """スタンプメッセージへの返答"""
    print(f"event.reply_token = {event.reply_token}")
    print(f"event.postback = {event.postback}")
    print(f"event.postback.data = {event.postback.data}")
    print(f"event.postback.params = {event.postback.params}")
    print(f"event.source = {event.source}")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=json.dumps(json.loads(event.postback.data), indent=2)))
    # line_bot_api.push_message(event.source.user_id, TextSendMessage(text="push"))


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """テキストメッセージへの返答"""
    rich_menu_list = line_bot_api.get_rich_menu_list()
    print(rich_menu_list)
    print(event.source.user_id)
    if event.message.text == "プロフィール":
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=json.dumps(json.loads(str(line_bot_api.get_profile(event.source.user_id))), indent=2)),
            TemplateSendMessage(alt_text="alt_text", template=ButtonsTemplate(text="テキスト", title="タイトル")),
            TemplateSendMessage(alt_text="alt_text",
                                template=ButtonsTemplate(text="全角11～14文字",
                                                         actions=[
                                                             MessageAction(
                                                                 label="あああああああああああ",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="ああああああああああああ",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="あああああああああああああ",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="ああああああああああああああ",
                                                                 text="text2")])),
            TemplateSendMessage(alt_text="alt_text",
                                template=ButtonsTemplate(text="半角17～20文字",
                                                         actions=[
                                                             MessageAction(
                                                                 label="ABCDEFGHIJKLMNOPQ",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="ABCDEFGHIJKLMNOPQR",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="ABCDEFGHIJKLMNOPQRS",
                                                                 text="text2"),
                                                             MessageAction(
                                                                 label="ABCDEFGHIJKLMNOPQRST",
                                                                 text="text2")]))])
    elif event.message.text == "テキスト2":
        line_bot_api.link_rich_menu_to_user(event.source.user_id, "richmenu-c1de37420fa93446ac77f889197c11ef")
    else:
        line_bot_api.link_rich_menu_to_user(event.source.user_id, 'richmenu-d00f0b8536f5e6f0e62fff2bfc528895')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="text"))
