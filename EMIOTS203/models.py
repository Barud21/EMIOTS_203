from django.db import models


class TweetAndStockChart(models.Model):
    tweetHtmlContent = models.TextField(null=False, blank=False)
    chartHtmlContent = models.TextField(null=False, blank=False)
    maxStockChange = models.FloatField()
    publish_date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False)

    class Meta:
        ordering = ['-publish_date']
