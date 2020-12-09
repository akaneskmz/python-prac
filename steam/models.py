from django.db import models


# Create your models here.

class LastUnlockAchievement(models.Model):
    last_unlock_time = models.IntegerField()


class App(models.Model):
    app_id = models.IntegerField()
    name = models.CharField(max_length=256)
