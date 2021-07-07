from django.db import models

# Create your models here.
from django.db.models import DateTimeField, TextField


class KindleShare(models.Model):
    add_date = DateTimeField()
    content = TextField()
    share_date = DateTimeField(null=True)
