from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class User(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.TextField(null=False)
#     profile_pic = models.TextField(null=False, default="https://pbs.twimg.com/media/GN_WWe5aUAAZk-S?format=jpg&name=4096x4096")
#     date_created = models.DateTimeField(auto_now_add=True)

class Transcribe(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcribe', default=1)
    title = models.TextField(null=False, default="none")
    trans_result = models.TextField(null=False)
    date_created = models.DateTimeField(auto_now_add=True)


class Sentences(models.Model):
    class SATag(models.TextChoices) :
        NEGATIVE = 'N', 'Negative'
        NEUTRAL = 'O', 'Neutral'
        POSITIVE = 'P', 'Positive'
    id = models.AutoField(primary_key=True)
    id_trans = models.ForeignKey(Transcribe, on_delete=models.CASCADE, related_name='sentence', default=1)
    sentence = models.TextField(null=False)
    positive = models.DecimalField(max_digits=5, decimal_places=3, default=0.0)
    negative = models.DecimalField(max_digits=5, decimal_places=3, default=0.0)
    neutral = models.DecimalField(max_digits=5, decimal_places=3, default=0.0)
    sa_tag = models.CharField(max_length=1, choices=SATag.choices, default=SATag.NEUTRAL)

