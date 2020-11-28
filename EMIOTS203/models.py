from django.db import models


class Tweet(models.Model):
    externalId = models.BigIntegerField(primary_key=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False)
    text = models.TextField(null=False, blank=False)
    retweets = models.IntegerField(null=False)
    favorites = models.IntegerField(null=False)
    tweetHtml = models.TextField(null=False, blank=False)

    class Meta:
        ordering = ['-date']


class StockChart(models.Model):
    chartHtml = models.TextField(null=False, blank=False)
    maxSwing = models.FloatField()
    tweetId = models.OneToOneField(
        Tweet,
        on_delete=models.CASCADE,
        primary_key=True,
    )
