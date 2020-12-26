import requests

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
