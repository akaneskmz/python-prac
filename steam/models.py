from django.db import models


# Create your models here.

class LastUnlockAchievement(models.Model):
    last_unlock_time = models.IntegerField()


class App(models.Model):
    """ゲームデータ"""
    app_id = models.IntegerField()
    name = models.CharField(max_length=256)


class Achievement(models.Model):
    """実績"""
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    api_name = models.CharField(max_length=256)
    achieved = models.BooleanField()
    unlock_time = models.DateTimeField()
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    icon = models.URLField()
    hidden = models.BooleanField()


class OwnedGames(models.Model):
    """所持ゲーム"""
    data = models.JSONField()


class GameList(models.Model):
    """ゲームリスト"""
    data = models.JSONField()
