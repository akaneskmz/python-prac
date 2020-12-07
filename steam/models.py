from django.db import models


# Create your models here.

class LastUnlockAchievement(models.Model):
    last_unlock_time = models.IntegerField()
