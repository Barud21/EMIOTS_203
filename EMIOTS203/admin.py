from django.contrib import admin

from .models import Tweet, StockChart

# Register your models here.
admin.site.register(Tweet)
admin.site.register(StockChart)
